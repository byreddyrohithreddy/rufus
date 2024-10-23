from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
import os
from inscriptis import get_text
from langchain.docstore.document import Document
from langchain_community.vectorstores import DocArrayInMemorySearch
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from urllib.parse import  urlparse, urljoin
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

os.environ["GOOGLE_API_KEY"] = "your_api_key"
llm = ChatGoogleGenerativeAI(model="gemini-pro")
gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
parser = StrOutputParser()

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str
    instructions: str

def fetch_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def navigate_page(url):
    try:
        content = fetch_content(url)
        return BeautifulSoup(content, "html.parser")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred for {url}: {str(http_err)}")
        raise ValueError(f"HTTP error: {str(http_err)}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Error occurred while fetching {url}: {str(req_err)}")
        raise ValueError(f"Request error: {str(req_err)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise ValueError(f"Unexpected error: {str(e)}")

def is_html_link(link):
    parsed_url = urlparse(link)
    return parsed_url.path.endswith(('.html', '.htm'))

# def crawl(start_url):
#     data = []
    
#     try:
#         soup = navigate_page(start_url)
#     except ValueError as e:
#         logging.error(f"Failed to navigate to start URL: {str(e)}")
#         return []

#     soup_text = get_text(str(soup))
#     data.append(soup_text)

#     relevant_links = [
#         a['href'] for a in soup.find_all('a', href=True)
#         if is_html_link(a['href'])
#     ]

#     for link in relevant_links:
#         try:
#             nested_soup = navigate_page(link)
#             nested_text = get_text(str(nested_soup))
#             data.append(nested_text)
#         except ValueError as e:
#             logging.warning(f"Skipping link {link} due to error: {str(e)}")

#     return data

async def crawl(start_url,instructions):
    data = []
    async with async_playwright() as p:
    
        browser = await p.chromium.launch(headless=False) 
        page = await browser.new_page()

        await page.goto(start_url)

        await page.wait_for_load_state('networkidle')

        html_content = await page.content()

        soup_text = get_text(str(html_content))
        data.append(soup_text)

        links = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a')).map(a => a.href);
        }''')

        valid_links = []
        for link in links:
            if link.startswith('http') and (link.endswith('.html') or link.endswith('/')):
                valid_links.append(link)
            elif link.startswith('/'):
                full_link = urljoin(start_url, link)
                valid_links.append(full_link)

        str_valid_links = '\n'.join(valid_links)

        template1 = """Below are the some of the internal links extracted from a webpage, you need to identify the 
                        html links which are relevant to the prompt below and provide the relevant links as a string list like link1,link2,....
                        if there is none provide response empty
                    
                     internal links: \n\n{context}\n\n 
                    
                     prompt: \n{question}"""

        prompt = PromptTemplate.from_template(template1)
    
        response = llm.invoke(prompt.format(context=str_valid_links, question=instructions))
        response_links = str(response.content).split(",")

        for link in response_links:
            if link=="empty":
                break
            try:
                await page.goto(link)
                await page.wait_for_load_state('networkidle')

                html_link_content = await page.content()
                soup_link_text = get_text(str(html_link_content))
                data.append(soup_link_text)

            except ValueError as e:
                logging.warning(f"Skipping link {link} due to error: {str(e)}")
        
        await browser.close()
    return data 

@app.post("/scrape")
async def scrape_website(scrape_request: ScrapeRequest, authorization: str = Header(None)):
    expected_api_key = "12345678"
    if authorization != f"Bearer {expected_api_key}":
        logging.error("Invalid API key")
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    url = scrape_request.url
    instructions = scrape_request.instructions
    try:
        response =await crawl(url,instructions)
        if not response:
            raise HTTPException(status_code=400, detail="No content fetched from the URL")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")

    concatenated_response = "\n".join(response)

    template = """You are data extraction agent, extract info from the below response relevant to the prompt.
                
                 Response: \n\n{response}\n\n 
                
                prompt \n{instructions}"""

    prompt = PromptTemplate.from_template(template)

    docs = [Document(page_content=concatenated_response, metadata={"source": "local"})]

    try:
        vectorstore = DocArrayInMemorySearch.from_documents(docs, embedding=gemini_embeddings)
        retriever = vectorstore.as_retriever()
        
        chain = (
            {
                "response": itemgetter("instructions") | retriever,
                "instructions": itemgetter("instructions"),
            }
            | prompt
            | llm
            | parser
        )

        out = chain.invoke({'instructions': instructions})
    except Exception as e:
        logging.error(f"Error during LLM processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing request with LLM")

    return {
        "content": out
    }

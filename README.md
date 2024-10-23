# Rufus Web Scraper Documentation

## Overview

Rufus is a web scraping application that utilizes FastAPI for creating a web service to scrape content from specified URLs. It allows users to send requests with instructions on what data to extract from the webpages. The extracted data is processed using LangChain's language models and can be saved in different file formats.

## Features

- **API-Based Scraping**: Users can send POST requests to the FastAPI server to scrape content from a specified URL.
- **Custom Instructions**: Users can specify instructions to guide the data extraction process.
- **Multiple Output Formats**: The extracted content can be saved as plain text, Markdown, or JSON files.
- **Error Handling**: Comprehensive error logging and handling for various HTTP and network-related issues.

## Methodology:

## Web scraping:
- When provided with a URL and a prompt, the web scraper should provide relevant information related to the prompt. Usually, any web scraper extracts information from only the page it has been provided.
- A common challenge for any web search is not scraping the entire web associated with the website. To solve this, nested web link identification and extraction of information from all specified links are employed.
- Identifying nested links and gathering information from all corners of the website is a general methodology, but it takes a lot of time to scrape. Larger websites require significantly more time to scrape.
- BeautifulSoup was used as the web scraper, which utilizes HTTP requests for scraping. BeautifulSoup is a basic library for extracting website information but cannot load dynamic content from JavaScript.
- In the future, advanced frameworks like Playwright or Scrapy will be employed for extracting dynamic content from websites and for efficient data searches for targeted information.
  
## RAG application:
- After compiling information from the websites, efficient search methodologies are deployed to extract relevant information based on the prompt. LLMs and RAG applications are used to facilitate efficient searches.
- Vectorizing the entire search results will help search for other information in the future; thus, InMemorySearch was employed, but there is potential to move to cloud vectors like Qdrant for cleaner and more efficient vectorization.
- Conducting similarity searches is important to extract information relevant to the prompt. After performing a similarity search, relevant information needed by the end user is retrieved.
- The similarity search results are passed through a specialized prompt template to gather the necessary information. The final information retrieved from the LLM is the end result. Gemini Pro LLM was used, but on-prem LLMs from Ollama or other existing LLMs can also be utilized.

## FastAPI:
- FastAPI was leveraged because it offers a lot of features with lightweight functions.
- FastAPI can be deployed easily on any web server.
- It employs API validation techniques as well as user authentication features for future needs.
- It can easily connect with databases as well as cloud APIs.

## Project Structure

```plaintext
.
├── main.py                # FastAPI application for scraping
├── client.py              # Client to interact with the FastAPI application
└── README.md              # Project documentation
```

## Requirements
Make sure to have the following libraries installed:

```bash
pip install fastapi uvicorn beautifulsoup4 requests langchain google-generative-ai inscriptis
```

## Getting Started
## Running the FastAPI Application
1. Clone the repository and navigate to the project directory.
2. Set your Google API key in the `main.py` file:

```python
os.environ["GOOGLE_API_KEY"] = "Your_api_key"
```

3. Start the FastAPI application:
```bash
uvicorn main:app --reload
```
4. The API will be available at `http://127.0.0.1:8000`.

## Using the Client
1. Import the `RufusClient` in your script:

```python
from rufus import RufusClient
```

2. Initialize the client with your API key:
```python
client = RufusClient(api_key="12345678")
```
3. Call the `scrape` method with the desired URL and instructions:
```python
instructions = "Get headlines of all news"
result = client.scrape("https://news.ycombinator.com/", instructions)
```
4. Save the content to a file using the `save_to_file` method:
```python
client.save_to_file(result, "text.txt")
```

## API Endpoints

## `POST /scrape`

- **Request Body:**
```
{
    "url": "https://example.com",
    "instructions": "Extract specific data"
}
```
- **Headers:**
  - `Authorization`: Bearer token (e.g.,  `Bearer 12345678`)
- **Response:**
  - **Status Code:** 200 OK
  - **Body:**
    ```
    {
    "content": "Extracted content from the webpage"
    }
    ```

- **Error Codes:**
  - 403 Forbidden: Invalid API key.
  - 400 Bad Request: Issues with the URL or no content found.
  - 500 Internal Server Error: Errors during processing.

## File Formats Supported

- **.txt:** Plain text format.
- **.md:** Markdown format with a header.
- **.json:** JSON format for structured content.

## Example Usage
Here is an example of how to use the `RufusClient` to scrape a website and save the results:

```python
from rufus import RufusClient

client = RufusClient(api_key="12345678")
instructions = "Get headlines of all news"
result = client.scrape("https://news.ycombinator.com/", instructions)

client.save_to_file(result, "text.txt")
```

## Logging
The application uses the `logging` library to provide detailed logs for debugging and monitoring purposes. Logs are generated for:

- HTTP errors
- Request failures
- Unexpected exceptions during the scraping and processing phases

## Conclusion

Rufus is a powerful tool for web scraping, providing a simple yet effective way to extract information from webpages based on user-defined instructions. It leverages the capabilities of FastAPI and LangChain to create a robust solution for data extraction tasks.

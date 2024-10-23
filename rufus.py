import requests
import json

class RufusClient:
    def __init__(self, api_key: str, base_url: str = "http://127.0.0.1:8000"):
        self.api_key = api_key
        self.base_url = base_url

    def scrape(self, url: str, instructions: str):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "url": url,
            "instructions": instructions
        }
        response = requests.post(f"{self.base_url}/scrape", json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.json().get('detail', 'Unknown Error')}")
        
        content = response.json().get("content")
        return content
    
    def save_to_file(self, content: str, filename: str):

        if not content.strip():
            print("Warning: The content is empty. No file will be created.")
            return
    
        file_extension = filename.split('.')[-1]

        try:
            if file_extension == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            elif file_extension == 'md':
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# Scraped Content\n\n{content}")
            elif file_extension == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({"content": content}, f, ensure_ascii=False, indent=4)
            else:
                raise ValueError("Unsupported file format. Please use .txt, .md, or .json.")
            print(f"Content saved to {filename}")
        except Exception as e:
            print(f"Failed to save content to {filename}: {str(e)}")


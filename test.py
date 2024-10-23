
from rufus import RufusClient

client = RufusClient(api_key="12345678")
instructions = "Get headlines of all news"
result = client.scrape("https://news.ycombinator.com/", instructions)

client.save_to_file(result,"text.txt")

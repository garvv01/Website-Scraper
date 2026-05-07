from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import json

# Load the API key

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

# Connect to firecrawl

app = FirecrawlApp(api_key=api_key)

# Take url as input

url = input("Enter website URL: ")

# Scrape the website from firecrawl

scrape_result = app.scrape(
    url,
    formats=["markdown"],
    only_main_content=True
)

# Store the result in a json file

with open("data.json", "w") as f:
    json.dump(scrape_result.model_dump(), f, indent=2)

print("Scraping complete.")
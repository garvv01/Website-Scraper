from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import time

load_dotenv()

app = FirecrawlApp(
    api_key=os.getenv("FIRECRAWL_API_KEY")
)

def scrape_url(url, retries=3):

    for attempt in range(retries):

        try:

            result = app.scrape(
                url,
                formats=["markdown"],
                only_main_content=True
            )

            data = result.model_dump()

            return data.get("markdown", "")

        except Exception as e:

            print(f"Attempt {attempt+1} failed: {e}")

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    raise Exception("Scraping failed after retries")
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import json
from difflib import SequenceMatcher
import re

# Load the API key

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

# Connect to firecrawl

app = FirecrawlApp(api_key=api_key)

# Cleaning function

def clean_markdown(md):

    # Remove Image Markdown
    md = re.sub(r'!\[.*?\]\(.*?\)', '', md)

    # Remove links but keep text
    md = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', md)

    # Remove extra whitespace
    md = re.sub(r'\n\s*\n+', '\n\n', md)

    # Split into lines
    lines = md.splitlines()

    cleaned = []
    seen = set()

    # Generic junk patterns
    junk_patterns = [
        r'cookie',
        r'privacy policy',
        r'terms of service',
        r'all rights reserved',
        r'subscribe',
        r'sign up',
        r'log in',
        r'login',
        r'apply now',
        r'click here',
        r'view all',
        r'learn more',
        r'read more',
        r'contact us',
        r'follow us',
        r'share this',
        r'copyright',
        r'your browser does not support',
    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        normalized = line.lower()

        # Remove junk phrases
        if any(re.search(pattern, normalized) for pattern in junk_patterns):
            continue

        # Remove very short lines
        if len(line) < 4:
            continue

        # Remove low letter lines
        if len(re.findall(r'[a-zA-Z]', line)) < 3:
            continue

        # Remove lines with too many symbols
        symbol_ratio = len(re.findall(r'[^a-zA-Z0-9\s]', line)) / len(line)

        if symbol_ratio > 0.4:
            continue

        # Remove duplicate lines
        if normalized in seen:
            continue

        seen.add(normalized)

        cleaned.append(line)

    # Paragraph duplication
    unique = []

    for para in cleaned:

        duplicate = False

        for existing in unique:

            similarity = SequenceMatcher(
                None,
                para,
                existing
            ).ratio()

            if similarity > 0.9:
                duplicate = True
                break

        if not duplicate:
            unique.append(para)

    return "\n".join(unique)

# Take url as input

url = input("Enter website URL: ")

# Scrape the website from firecrawl

scrape_result = app.scrape(
    url,
    formats=["markdown"],
    only_main_content=True
)

# Convert to dictionary

data = scrape_result.model_dump()

# Extract markdown

markdown = data.get("markdown", "")

# Clean markdown
cleaned_text = clean_markdown(markdown)

# Add cleaned content
data["cleaned_markdown"] = cleaned_text

# Save final output
with open("cleaned_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Scraping and cleaning complete.")
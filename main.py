from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import json
import re
from difflib import SequenceMatcher

# Load the API key

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

# Connect to firecrawl

app = FirecrawlApp(api_key=api_key)

# ── Pre-compiled patterns ─────────────────────────────────────────────

_JUNK_PHRASES = re.compile(
    r'\b('
    r'cookie[s]?|privacy policy|terms of service|terms & conditions|'
    r'all rights reserved|subscribe|sign up|sign in|log in|login|log out|'
    r'apply now|click here|view all|learn more|read more|contact us|'
    r'follow us|share this|copyright|your browser does not support|'
    r'get started|buy now|free trial|download now|try for free|'
    r'get in touch|request a demo|book a demo|schedule a call|'
    r'back to top|skip to content|skip to main|'
    r'newsletter|unsubscribe|manage preferences|'
    r'add to cart|checkout|view cart|place order|'
    r'powered by|built with|made with'
    r')\b',
    re.IGNORECASE
)

_NAV_LABEL = re.compile(r'^[A-Z][a-zA-Z\s&/\-]{0,30}$')

_HEADING = re.compile(r'^#{1,6}\s+(.+)$')

_DIVIDER = re.compile(r'^[-*_]{3,}\s*$')

_LIST_ITEM = re.compile(r'^[-*+]\s+|^\d+\.\s+')

_NO_WORDS = re.compile(r'^[^a-zA-Z]*$')

_SOCIAL = re.compile(r'@\w+|#\w+')

# ── Helper functions ─────────────────────────────────────────────────

def _word_count(line):
    return len(line.split())

def _is_nav_label(line):
    stripped = _LIST_ITEM.sub('', line).strip()
    words = stripped.split()

    if len(words) == 0 or len(words) > 5:
        return False

    if re.search(r'[.!?]$', stripped):
        return False

    return bool(_NAV_LABEL.match(stripped))

def _is_link_cluster_block(lines):

    if len(lines) < 3:
        return False

    nav_count = sum(
        1 for l in lines
        if _is_nav_label(_LIST_ITEM.sub('', l).strip())
    )

    return nav_count / len(lines) >= 0.6

def _fuzzy_duplicate(line, seen_lines, threshold=0.82):

    for existing in seen_lines:

        similarity = SequenceMatcher(
            None,
            line,
            existing
        ).ratio()

        if similarity >= threshold:
            return True

    return False

def _extract_heading_text(line):

    match = _HEADING.match(line)

    return match.group(1) if match else line

# ── Main cleaning function ───────────────────────────────────────────

def clean_markdown(md):

    # Remove image markdown
    md = re.sub(r'!\[.*?\]\(.*?\)', '', md)

    # Remove links but keep text
    md = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', md)

    # Remove raw URLs
    md = re.sub(r'https?://\S+', '', md)

    # Remove excessive blank lines
    md = re.sub(r'\n{3,}', '\n\n', md)

    lines = md.splitlines()

    # Detect nav/footer blocks
    block_size = 5
    junk_line_indices = set()

    for i in range(len(lines) - block_size + 1):

        window = [
            lines[j].strip()
            for j in range(i, i + block_size)
            if lines[j].strip()
        ]

        if _is_link_cluster_block(window):

            for j in range(i, i + block_size):
                junk_line_indices.add(j)

    filtered = []

    seen_exact = set()

    seen_fuzzy = []

    for idx, raw_line in enumerate(lines):

        line = raw_line.strip()

        # Keep paragraph spacing
        if not line:
            filtered.append('')
            continue

        # Remove nav/footer clusters
        if idx in junk_line_indices:
            continue

        normalized = line.lower()

        # Remove dividers
        if _DIVIDER.match(line):
            continue

        # Remove social spam
        if len(_SOCIAL.findall(line)) >= 2:
            continue

        # Remove junk phrases
        if _JUNK_PHRASES.search(normalized):
            continue

        # Handle headings
        if _HEADING.match(line):

            heading_text = _extract_heading_text(line)

            if (
                _word_count(heading_text) <= 3 and
                not re.search(r'[.!?]', heading_text)
            ):
                continue

            line = heading_text

        # Remove symbol-only lines
        if _NO_WORDS.match(line):
            continue

        # Remove tiny lines
        if len(line) < 15 and not re.search(r'\d', line):
            continue

        # Remove low-letter lines
        if len(re.findall(r'[a-zA-Z]', line)) < 3:
            continue

        # Remove symbol-heavy lines
        symbol_ratio = (
            len(re.findall(r'[^a-zA-Z0-9\s]', line))
            / max(len(line), 1)
        )

        if symbol_ratio > 0.40:
            continue

        # Remove nav labels
        if _is_nav_label(line):
            continue

        # Exact duplicate removal
        if normalized in seen_exact:
            continue

        seen_exact.add(normalized)

        # Fuzzy duplicate removal
        if len(line) > 40:

            if _fuzzy_duplicate(normalized, seen_fuzzy):
                continue

            seen_fuzzy.append(normalized)

            # Keep memory small
            if len(seen_fuzzy) > 300:
                seen_fuzzy = seen_fuzzy[-200:]

        filtered.append(line)

    # Rebuild clean paragraphs
    result_lines = []

    prev_blank = False

    for line in filtered:

        if line == '':

            if not prev_blank:
                result_lines.append('')

            prev_blank = True

        else:
            result_lines.append(line)
            prev_blank = False

    return '\n'.join(result_lines).strip()

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
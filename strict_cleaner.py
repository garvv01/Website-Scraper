import re
from difflib import SequenceMatcher

JUNK_HEADINGS = {
    "related articles",
    "comments",
    "quick links",
    "other links",
    "social media links",
    "subscribe to our newsletter",
    "get support",
}

def fuzzy_duplicate(line, seen, threshold=0.92):

    for old in seen:
        if SequenceMatcher(None, line, old).ratio() >= threshold:
            return True

    return False


def is_probable_junk_block(block):

    if len(block) < 3:
        return False

    short_lines = sum(len(x.strip()) < 40 for x in block)

    junk_lines = sum(
        any(j in x.lower() for j in [
            "subscribe",
            "comments",
            "related articles",
            "quick links",
            "follow us",
            "social media"
        ])
        for x in block
    )

    return (
        short_lines / len(block) > 0.8
        and junk_lines >= 2
    )


def clean_markdown(md):

    md = re.sub(r'!\[.*?\]\(.*?\)', '', md)
    md = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', md)

    lines = md.splitlines()

    blocks = []
    current = []

    for line in lines:

        if line.strip():
            current.append(line)

        else:
            if current:
                blocks.append(current)
                current = []

    if current:
        blocks.append(current)

    cleaned_blocks = []

    seen = []

    for block in blocks:

        if is_probable_junk_block(block):
            continue

        cleaned = []

        for line in block:

            stripped = line.strip()

            if not stripped:
                continue

            lower = stripped.lower()

            if lower in JUNK_HEADINGS:
                continue

            if len(stripped) > 60:
                if fuzzy_duplicate(lower, seen):
                    continue

                seen.append(lower)

            cleaned.append(stripped)

        if cleaned:
            cleaned_blocks.append("\n".join(cleaned))

    return "\n\n".join(cleaned_blocks)
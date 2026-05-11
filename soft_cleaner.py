import re

def clean_markdown(md):

    md = re.sub(r'!\[.*?\]\(.*?\)', '', md)

    md = re.sub(
        r'\[(.*?)\]\(.*?\)',
        r'\1',
        md
    )

    md = re.sub(r'\n{3,}', '\n\n', md)

    return md.strip()
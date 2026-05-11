from scrapers.scraper import scrape_url
from cleaners.strict_cleaner import clean_markdown as strict_clean
from cleaners.soft_cleaner import clean_markdown as soft_clean
from pathlib import Path
from utils.link_discovery import discover_links

URLS = [
    "https://www.sequoiacap.com"
]

output_dir = Path("output")

output_dir.mkdir(exist_ok=True)

for idx, url in enumerate(URLS, start=1):

    print(f"Processing {url}")

    markdown = scrape_url(url)

    print(markdown[:3000])

    discovered_links = discover_links(
        markdown,
        url
    )

    print(discovered_links)

    strict_output = strict_clean(markdown)

    soft_output = soft_clean(markdown)

    run_dir = output_dir / f"run{idx}"

    run_dir.mkdir(exist_ok=True)

    with open(run_dir / "url_used.txt", "w") as f:
        f.write(url)

    with open(run_dir / "strict_output.md", "w") as f:
        f.write(strict_output)

    with open(run_dir / "soft_output.md", "w") as f:
        f.write(soft_output)

    print(f"Saved outputs for run{idx}")
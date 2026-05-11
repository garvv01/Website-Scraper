from scraper import scrape_url
from strict_cleaner import clean_markdown as strict_clean
from soft_cleaner import clean_markdown as soft_clean

from pathlib import Path

URLS = [
    "https://www.schoolnetindia.com/blog/6-reasons-why-edtech-companies-in-india-struggle/",
    "https://www.iipa.org.in/GyanKOSH/posts/the-dark-side-a-look-at-indias-edtech-landscape",
    "https://www.tatvasoft.com/outsourcing/2022/07/edtech-challenges.html"
]

output_dir = Path("output")

output_dir.mkdir(exist_ok=True)

for idx, url in enumerate(URLS, start=1):

    print(f"Processing {url}")

    markdown = scrape_url(url)

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
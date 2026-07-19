"""
Airtel B2B Page Scraper
Scrapes public Airtel B2B product and solution pages and saves them to data/raw/.
Logs blocked/JS-rendered/inaccessible pages in MISSING_DATA.md.
"""

import os
import re
import time
from typing import List, Set, Dict, Tuple
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")
MISSING_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "MISSING_DATA.md")

SEED_URLS = [
    "https://www.airtel.in/b2b/",
    "https://www.airtel.in/b2b/airtel-iq/",
    "https://www.airtel.in/b2b/connectivity/",
    "https://www.airtel.in/b2b/cloud/",
    "https://www.airtel.in/b2b/cyber-security/",
    "https://www.airtel.in/b2b/data-center/",
    "https://www.airtel.in/b2b/iot/",
    "https://www.airtel.in/b2b/sd-wan/",
    "https://www.airtel.in/b2b/internet-leased-line/",
    "https://www.airtel.in/b2b/mpls/",
    "https://www.airtel.in/b2b/cpaas/",
    "https://www.airtel.in/b2b/solutions/work-from-home",
    "https://www.airtel.in/b2b/services/voice/",
    "https://www.airtel.in/b2b/services/corporate-postpaid/",
    "https://www.airtel.in/b2b/services/toll-free-number/",
    "https://www.airtel.in/b2b/services/sip-trunk/",
    "https://www.airtel.in/b2b/services/cloud-portfolio/",
    "https://www.airtel.in/b2b/services/colocation/",
    "https://www.airtel.in/b2b/services/cyber-security/",
    "https://www.airtel.in/b2b/services/iot/",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def url_to_slug(url: str) -> str:
    path = urlparse(url).path.strip('/')
    if not path or path == "b2b":
        return "b2b_home"
    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', path)
    return slug

def init_missing_data_file():
    os.makedirs(os.path.dirname(MISSING_DATA_FILE), exist_ok=True)
    header = "# Missing & Inaccessible Data Log\n\nLog of Airtel B2B URLs that were blocked, restricted by robots/JS rendering, or required login/authentication.\n\n| URL | Reason / Error | Date Logged | Impact |\n|---|---|---|---|\n"
    with open(MISSING_DATA_FILE, "w", encoding="utf-8") as f:
        f.write(header)

def log_missing_data(url: str, reason: str):
    today = time.strftime("%Y-%m-%d")
    log_entry = f"| {url} | {reason} | {today} | Missing product/solution details |\n"
    
    if os.path.exists(MISSING_DATA_FILE):
        with open(MISSING_DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if url not in content:
            with open(MISSING_DATA_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
    else:
        init_missing_data_file()
        with open(MISSING_DATA_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)

def clean_html_to_markdown(html_content: str, url: str) -> str:
    try:
        soup = BeautifulSoup(html_content, "lxml")
    except Exception:
        soup = BeautifulSoup(html_content, "html.parser")
    
    for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
        tag.decompose()
        
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url_to_slug(url)
    
    lines = [f"<!-- Source URL: {url} -->", f"# {title}\n"]
    
    main_content = soup.find("main") or soup.find("body") or soup
    
    for elem in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'td']):
        text = elem.get_text(strip=True)
        if not text or len(text) < 3:
            continue
        
        name = elem.name
        if name == 'h1':
            lines.append(f"\n# {text}\n")
        elif name == 'h2':
            lines.append(f"\n## {text}\n")
        elif name == 'h3':
            lines.append(f"\n### {text}\n")
        elif name == 'h4':
            lines.append(f"\n#### {text}\n")
        elif name == 'li':
            lines.append(f"- {text}")
        else:
            lines.append(text)
            
    return "\n".join(lines)

def extract_b2b_links(html_content: str, base_url: str) -> Set[str]:
    soup = BeautifulSoup(html_content, "html.parser")
    found_urls = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc.endswith("airtel.in") and "/b2b" in parsed.path:
            if not any(parsed.path.endswith(ext) for ext in ['.pdf', '.png', '.jpg', '.jpeg', '.css', '.js']):
                found_urls.add(full_url.split('#')[0])
    return found_urls

def scrape_airtel_b2b() -> Tuple[int, List[str]]:
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    init_missing_data_file()
    
    # Clean previous raw dir
    for existing_file in os.listdir(RAW_DATA_DIR):
        if existing_file.endswith(('.md', '.txt')):
            os.remove(os.path.join(RAW_DATA_DIR, existing_file))
            
    visited_urls: Set[str] = set()
    to_visit: List[str] = list(SEED_URLS)
    successful_files: List[str] = []
    
    while to_visit and len(visited_urls) < 40:
        url = to_visit.pop(0)
        if url in visited_urls:
            continue
        visited_urls.add(url)
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                log_missing_data(url, f"HTTP Status {resp.status_code}")
                continue
                
            content = resp.text
            if "loaderInfo" in content or "Loading…Please Wait" in content:
                log_missing_data(url, "JS-rendered SPA page (requires client-side JavaScript execution)")
                continue
                
            md_content = clean_html_to_markdown(content, url)
            clean_text = re.sub(r'<!--\s*Source URL:\s*.*?\s*-->', '', md_content).strip()
            
            if len(clean_text) < 300:
                log_missing_data(url, "Insufficient static HTML text (JS-rendered content)")
                continue
                
            slug = url_to_slug(url)
            file_path = os.path.join(RAW_DATA_DIR, f"{slug}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            successful_files.append(file_path)
            
            discovered = extract_b2b_links(content, url)
            for d_url in discovered:
                if d_url not in visited_urls and d_url not in to_visit:
                    to_visit.append(d_url)
                    
            time.sleep(0.3)
            
        except Exception as e:
            log_missing_data(url, f"Network/Scrape exception: {str(e)}")
            
    return len(successful_files), successful_files

if __name__ == "__main__":
    count, files = scrape_airtel_b2b()
    print(f"Scraped {count} pages successfully into {RAW_DATA_DIR}")

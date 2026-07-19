"""
Unit and Integration Tests for Phase 1 (Data Collection & Processing)
"""

import os
import json
import pytest
from src.data.scraper import url_to_slug, clean_html_to_markdown
from src.data.ingest import chunk_text, extract_source_url, process_raw_documents, OUTPUT_CHUNKS_FILE, RAW_DATA_DIR

def test_url_to_slug():
    assert url_to_slug("https://www.airtel.in/b2b/") == "b2b_home"
    assert url_to_slug("https://www.airtel.in/b2b/airtel-iq/") == "airtel-iq"
    assert url_to_slug("https://www.airtel.in/b2b/connectivity/sd-wan") == "connectivity_sd-wan"

def test_extract_source_url():
    sample_content = "<!-- Source URL: https://www.airtel.in/b2b/sd-wan/ -->\n# SD-WAN Solution\nAirtel SD-WAN optimizes network traffic."
    url, cleaned = extract_source_url(sample_content)
    assert url == "https://www.airtel.in/b2b/sd-wan/"
    assert "<!-- Source URL:" not in cleaned
    assert "# SD-WAN Solution" in cleaned

def test_chunk_text():
    sample_text = ("Paragraph 1: Airtel Business provides high speed MPLS and SD-WAN networks.\n\n" * 10)
    chunks = chunk_text(sample_text, chunk_size=200, overlap=30)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 300

def test_clean_html_to_markdown():
    sample_html = """
    <html>
      <head><title>Airtel Cloud Services</title></head>
      <body>
        <script>console.log('ignore');</script>
        <main>
          <h1>Cloud Solutions</h1>
          <p>Airtel provides secure multi-cloud connectivity.</p>
        </main>
      </body>
    </html>
    """
    md = clean_html_to_markdown(sample_html, "https://www.airtel.in/b2b/cloud/")
    assert "<!-- Source URL: https://www.airtel.in/b2b/cloud/ -->" in md
    assert "# Cloud Solutions" in md
    assert "Airtel provides secure multi-cloud connectivity." in md
    assert "script" not in md.lower() or "ignore" not in md

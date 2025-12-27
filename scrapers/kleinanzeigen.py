"""
Kleinanzeigen.de scraper
"""

import re
import requests
from bs4 import BeautifulSoup

def scrape(url: str) -> dict:
    """
    Scrape a Kleinanzeigen.de listing
    Returns: {title, price, location, date, description, images[]}
    """
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        return None
    
    soup = BeautifulSoup(response.text, "lxml")
    html = response.text
    
    data = {
        "url": url,
        "title": "",
        "price": "",
        "location": "",
        "date": "",
        "description": "",
        "images": []
    }
    
    # === TITLE ===
    title_tag = soup.find("h1")
    if title_tag:
        data["title"] = title_tag.get_text(strip=True)
    
    # === PRICE ===
    price_tag = soup.find("h2")
    if price_tag:
        data["price"] = price_tag.get_text(strip=True)
    
    # === LOCATION & DATE ===
    # Look for pattern: "12345 City" and "01.01.2025"
    location_match = re.search(r"(\d{5}\s+[\w\s\-]+?)(?=\d{2}\.\d{2}\.\d{4}|$)", html)
    if location_match:
        data["location"] = location_match.group(1).strip()
    
    date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", html)
    if date_match:
        data["date"] = date_match.group(1)
    
    # === DESCRIPTION ===
    # Find description section
    desc_header = soup.find("h2", string=re.compile(r"Beschreibung", re.I))
    if desc_header:
        parent = desc_header.find_parent()
        if parent:
            # Get text after "Beschreibung"
            desc_text = parent.get_text(separator="\n", strip=True)
            desc_text = re.sub(r"^Beschreibung\s*", "", desc_text, flags=re.I)
            # Remove "Nachricht schreiben" and everything after
            desc_text = re.split(r"Nachricht schreiben", desc_text)[0]
            data["description"] = desc_text.strip()
    
    # === IMAGES ===
    # Find ALL images from the listing only (not related offers)
    # Images are in format: https://img.kleinanzeigen.de/api/v1/prod-ads/images/xx/xxxxx
    
    # Method 1: Find image IDs in the page source (most reliable)
    # These appear before the "Das könnte dich auch interessieren" section
    
    # Split HTML at "Das könnte dich auch interessieren" to exclude related listings
    main_content = html.split("Das könnte dich auch interessieren")[0] if "Das könnte dich auch interessieren" in html else html
    
    # Find all unique image IDs
    img_pattern = r"https://img\.kleinanzeigen\.de/api/v1/prod-ads/images/([a-f0-9]{2})/([a-f0-9\-]+)"
    found_images = re.findall(img_pattern, main_content)
    
    # Build full URLs and remove duplicates
    seen = set()
    for folder, img_id in found_images:
        full_url = f"https://img.kleinanzeigen.de/api/v1/prod-ads/images/{folder}/{img_id}?rule=$_57.AUTO"
        if img_id not in seen:
            seen.add(img_id)
            data["images"].append(full_url)
    
    return data


def download_image(url: str) -> bytes:
    """Download an image and return bytes"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    except:
        return None
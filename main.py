import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json

# File paths
path_to_file = r"D:\Users\Asus\Python\job\shoppin\\"
virgio_html = os.path.join(path_to_file, "virgio_source.txt")
virgio_csv = os.path.join(path_to_file, "virgio_products.csv")
westside_csv = os.path.join(path_to_file, "westside_products.json")

# Setup driver
def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Virgio: scroll and extract
def crawl_virgio():
    print("🚀 Crawling Virgio...")
    driver = setup_driver()
    driver.get("https://www.virgio.com/collections/all")
    time.sleep(2)

    last_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_scrolls = 0
    scroll_pause = 6
    scroll_step = 500
    max_wait = 15

    while True:
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            unchanged_scrolls += 1
        else:
            unchanged_scrolls = 0
            last_height = new_height

        print(f"📏 Scrolled to: {new_height}, unchanged: {unchanged_scrolls}")

        if unchanged_scrolls >= max_wait:
            print("✅ Reached end of page.")
            break

    with open(virgio_html, "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    driver.quit()
    print(f"📄 Virgio HTML saved to: {virgio_html}")

def extract_virgio():
    print("🔍 Extracting Virgio product links...")
    with open(virgio_html, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")
    anchors = soup.find_all("a", attrs={"data-discover": "true"})

    product_links = []
    for a in anchors:
        href = a.get("href")
        if href and href.startswith("/products/"):
            full_url = f"https://www.virgio.com{href}"
            product_links.append({"Product URL": full_url})

    df = pd.DataFrame(product_links).drop_duplicates()
    df.to_csv(virgio_csv, index=False)

    print(f"✅ Virgio: {len(df)} product links saved to {virgio_csv}")

# Westside (untouched)
def extract_westside_links():
    print("🌐 Extracting Westside links...")

    url = "https://www.westside.com/products/"
    driver = setup_driver()
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    section = soup.find("main", id="MainContent")
    parent_ul = section.find("ul", class_="collection-list") if section else None

    parent_anchors = parent_ul.find_all("a", class_="full-unstyled-link") if parent_ul else []
    parent_links = [f"https://www.westside.com{a['href']}" for a in parent_anchors if a.get("href")]

    product_links = set()

    for parent_url in parent_links:
        driver.get(parent_url)
        time.sleep(2)

        scroll_pause = 2
        scroll_step = 500
        unchanged_scrolls = 0
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                unchanged_scrolls += 1
            else:
                unchanged_scrolls = 0
                last_height = new_height

            if unchanged_scrolls >= 5:
                break

        inner_soup = BeautifulSoup(driver.page_source, "html.parser")
        anchors = inner_soup.find_all("a", class_="wizzy-result-product-item")
        for a in anchors:
            href = a.get("href")
            if href:
                product_links.add(href)

    driver.quit()

    with open(westside_csv, "w") as f:
        json.dump(list(product_links), f, indent=2)

    print(f"✅ Westside: {len(product_links)} product links saved to {westside_csv}")

# Run both
def main():
    crawl_virgio()
    extract_virgio()
    extract_westside_links()

if __name__ == "__main__":
    main()

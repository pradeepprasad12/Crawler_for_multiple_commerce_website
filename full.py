import os
import time
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

# Base paths
BASE_DIR = r"D:\Users\Asus\Python\job\shopping"
os.makedirs(BASE_DIR, exist_ok=True)

# === Setup Driver ===
def setup_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# === Virgio ===
def crawl_virgio():
    print("\n🚀 Crawling Virgio...")
    driver = setup_driver()
    driver.get("https://www.virgio.com/collections/all")
    time.sleep(2)

    last_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_scrolls = 0

    while True:
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(6)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            unchanged_scrolls += 1
        else:
            unchanged_scrolls = 0
            last_height = new_height

        if unchanged_scrolls >= 15:
            break

    soup = BeautifulSoup(driver.page_source, "lxml")
    anchors = soup.find_all("a", attrs={"data-discover": "true"})
    product_links = ["https://www.virgio.com" + a["href"] for a in anchors if a.get("href", "").startswith("/products/")]

    df = pd.DataFrame({"Source": "Virgio", "Product URL": list(set(product_links))})
    virgio_path = os.path.join(BASE_DIR, "virgio_products.csv")
    df.to_csv(virgio_path, index=False)
    print(f"✅ Virgio: {len(df)} products saved to {virgio_path}")
    driver.quit()

# === Westside ===
def extract_westside_links():
    print("\n🌐 Extracting Westside links...")
    driver = setup_driver()
    driver.get("https://www.westside.com/products/")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    section = soup.find("main", id="MainContent")
    anchors = section.select("ul.collection-list a.full-unstyled-link") if section else []
    category_links = ["https://www.westside.com" + a['href'] for a in anchors if a.get("href")]

    product_links = set()

    for link in category_links:
        driver.get(link)
        time.sleep(2)

        last_height = driver.execute_script("return document.body.scrollHeight")
        unchanged_scrolls = 0

        while True:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                unchanged_scrolls += 1
            else:
                unchanged_scrolls = 0
                last_height = new_height
            if unchanged_scrolls >= 15:
                break

        inner_soup = BeautifulSoup(driver.page_source, "html.parser")
        anchors = inner_soup.find_all("a", class_="wizzy-result-product-item")
        for a in anchors:
            href = a.get("href")
            if href:
                product_links.add("https://www.westside.com" + href)

    df = pd.DataFrame({"Source": "Westside", "Product URL": list(product_links)})
    westside_path = os.path.join(BASE_DIR, "westside_products.csv")
    df.to_csv(westside_path, index=False)
    print(f"✅ Westside: {len(df)} products saved to {westside_path}")
    driver.quit()

# === TataCliq ===
def fetch_tatacliq():
    print("\n📦 Crawling TataCliq...")
    driver = setup_driver()
    driver.get("https://www.tatacliq.com/sitemap")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    links = ["https://www.tatacliq.com" + a["href"] for a in soup.select("a.SitemapPage__link[href]") if a["href"].startswith("/") and a["href"] != "/"]
    product_links = set()

    for url in links:
        print(f"➡️ TataCliq URL: {url}")
        driver = setup_driver()
        try:
            driver.get(url)
            time.sleep(5)
            unchanged = 0

            while True:
                soup = BeautifulSoup(driver.page_source, "lxml")
                anchors = soup.select("#grid-container a[title][href^='/']")
                new_links = {"https://www.tatacliq.com" + a["href"] for a in anchors}

                before = len(product_links)
                product_links.update(new_links)
                after = len(product_links)

                if before == after:
                    unchanged += 1
                else:
                    unchanged = 0

                if unchanged >= 2:
                    break

                try:
                    show_more_btn = driver.find_element(By.CSS_SELECTOR, "button.ShowMoreButtonPlp__button")
                    driver.execute_script("arguments[0].click();", show_more_btn)
                except Exception:
                    break

                time.sleep(5)

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            driver.quit()

    df = pd.DataFrame({"Source": "TataCliq", "Product URL": list(product_links)})
    tata_path = os.path.join(BASE_DIR, "tatacliq_products.csv")
    df.to_csv(tata_path, index=False)
    print(f"✅ TataCliq: {len(df)} products saved to {tata_path}")

# === Nykaa Fashion ===
def fetch_nykaa():
    print("\n🛍️ Crawling Nykaa Fashion...")
    sitemap_url = "https://www.nykaafashion.com/cp/sitemap"
    driver = setup_driver()
    driver.get(sitemap_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    links = [(a.get_text(strip=True), "https://www.nykaafashion.com" + a["href"]) for a in soup.select("div.sitemap-wrapper.body-large a.link-level2")]

    all_products = []
    for name, url in links:
        driver = setup_driver()
        try:
            print(f"➡️ Nykaa URL: {url}")
            driver.get(url)
            time.sleep(3)

            product_urls = set()
            unchanged = 0

            while True:
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(5)
                soup = BeautifulSoup(driver.page_source, "lxml")
                product_div = soup.find("div", class_="css-bvydcl")
                if not product_div:
                    break

                anchors = product_div.find_all("a", href=True)
                new_links = {"https://www.nykaafashion.com" + a["href"] for a in anchors if a["href"].startswith("/")}

                if len(product_urls) == len(product_urls.union(new_links)):
                    unchanged += 1
                else:
                    product_urls.update(new_links)
                    unchanged = 0

                if unchanged >= 15:
                    break

            for link in product_urls:
                all_products.append({"Source": "Nykaa", "Product URL": link})
        except Exception as e:
            print(f"⚠️ Error on {url}: {e}")
        finally:
            driver.quit()

    df = pd.DataFrame(all_products).drop_duplicates()
    nykaa_path = os.path.join(BASE_DIR, "nykaa_products.csv")
    df.to_csv(nykaa_path, index=False)
    print(f"✅ Nykaa: {len(df)} products saved to {nykaa_path}")

# === MAIN ===
def main():
    crawl_virgio()
    extract_westside_links()
    fetch_tatacliq()
    fetch_nykaa()
    print("\n🎉 All stores scraped successfully!")

if __name__ == "__main__":
    main()

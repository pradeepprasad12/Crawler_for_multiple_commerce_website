import time
import os
import csv
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Paths
BASE_DIR = r"D:\Users\Asus\Python\job\shopping"
os.makedirs(BASE_DIR, exist_ok=True) 
sublinks_csv = os.path.join(BASE_DIR, "nykaa_sublinks.csv")
products_csv = os.path.join(BASE_DIR, "nykaa_products.csv")

# Config
sitemap_url = "https://www.nykaafashion.com/cp/sitemap"
scroll_pause = 5
scroll_step = 500
max_same_count = 15  # Break if product count doesn't increase for this many scrolls

# Setup driver
def setup_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Step 1: Scrape category links
def fetch_category_links():
    print("🔍 Fetching Nykaa sitemap category links...")
    driver = setup_driver()
    driver.get(sitemap_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    link_tags = soup.select("div.sitemap-wrapper.body-large a.link-level2")
    links = [{"Name": a.get_text(strip=True), "URL": "https://www.nykaafashion.com" + a["href"]} for a in link_tags]

    df = pd.DataFrame(links).drop_duplicates()
    df.to_csv(sublinks_csv, index=False)
    print(f"✅ Saved {len(df)} category links to {sublinks_csv}")

# Step 2: Scroll & scrape products from each category link
def fetch_product_links():
    print("🛒 Fetching products from each category...")
    df_links = pd.read_csv(sublinks_csv)
    all_products = []

    for _, row in df_links.iterrows():
        url = row["URL"]
        print(f"➡️ Scanning: {url}")
        driver = setup_driver()
        try:
            driver.get(url)
            time.sleep(3)

            product_urls = set()
            unchanged_count = 0

            while True:
                driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                time.sleep(scroll_pause)

                soup = BeautifulSoup(driver.page_source, "lxml")
                product_div = soup.find("div", class_="css-bvydcl")
                if not product_div:
                    print("❌ No product container found, skipping...")
                    break

                anchors = product_div.find_all("a", href=True)
                new_links = {
                    "https://www.nykaafashion.com" + a["href"]
                    for a in anchors if a["href"].startswith("/")
                }

                if len(product_urls) == len(product_urls.union(new_links)):
                    unchanged_count += 1
                else:
                    unchanged_count = 0
                    product_urls.update(new_links)

                print(f"🧮 Total Products Collected: {len(product_urls)}")

                if unchanged_count >= max_same_count:
                    print("✅ End reached or no more new products.")
                    break

            for link in product_urls:
                all_products.append({"Category": row["Name"], "Product URL": link})
            driver.quit()

        except Exception as e:
            print(f"⚠️ Error on {url}: {e}")
            driver.quit()

    df_all = pd.DataFrame(all_products).drop_duplicates()
    df_all.to_csv(products_csv, index=False)
    print(f"\n📦 Total {len(df_all)} products saved to {products_csv}")

# Main
if __name__ == "__main__":
    fetch_category_links()
    fetch_product_links()

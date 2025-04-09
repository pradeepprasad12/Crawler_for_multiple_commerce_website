import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

# Setup paths
base_path = r"D:\Users\Asus\Python\job\shoppin\tatacliq"
os.makedirs(base_path, exist_ok=True)
sublinks_csv = os.path.join(base_path, "tatacliq_sublinks.csv")
products_folder = os.path.join(base_path, "tatacliq_products")
os.makedirs(products_folder, exist_ok=True)
output_csv = os.path.join(products_folder, "tatacliq_all_products.csv")

# Setup driver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Step 1: Extract subcategory links
def fetch_sitemap_links():
    print("🔍 Fetching TataCliq sitemap subcategory links...")
    driver = setup_driver()
    driver.get("https://www.tatacliq.com/sitemap")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.quit()

    anchors = soup.select("a.SitemapPage__link[href]")
    links = []
    for a in anchors:
        href = a["href"]
        if href != "/" and href.startswith("/"):
            links.append("https://www.tatacliq.com" + href)

    df = pd.DataFrame({"SubLinks": list(set(links))})
    df.to_csv(sublinks_csv, index=False)
    print(f"✅ Found {len(df)} sublinks and saved to {sublinks_csv}")

# Step 2: Scrape product URLs
def scrape_products_from_links():
    print("🛒 Starting product scraping from each subcategory link...")
    df_links = pd.read_csv(sublinks_csv)

    for idx, row in df_links.iterrows():
        url = row["SubLinks"]
        print(f"\n➡️ Visiting: {url}")
        driver = setup_driver()

        try:
            driver.get(url)
            time.sleep(5)

            product_urls = set()
            unchanged_count = 0

            while True:
                soup = BeautifulSoup(driver.page_source, "lxml")
                anchors = soup.select("#grid-container a[title][href^='/']")
                current_urls = {f"https://www.tatacliq.com{a['href']}" for a in anchors}
                
                before_count = len(product_urls)
                product_urls.update(current_urls)
                after_count = len(product_urls)

                print(f"🔗 Found {after_count} product URLs so far")

                if after_count == before_count:
                    unchanged_count += 1
                else:
                    unchanged_count = 0

                if unchanged_count >= 2:
                    print("✅ No new products found. Moving to next link.")
                    break

                try:
                    show_more_btn = driver.find_element(By.CSS_SELECTOR, "button.ShowMoreButtonPlp__button")
                    driver.execute_script("arguments[0].click();", show_more_btn)
                    print("⏬ Clicked 'Show More Products'")
                except (NoSuchElementException, ElementClickInterceptedException):
                    print("⚠️ 'Show More Products' button not found or not clickable.")
                    break

                time.sleep(5)

            # Save results
            filename = os.path.join(products_folder, f"products_{idx+1}.csv")
            pd.DataFrame({"Product URLs": list(product_urls)}).to_csv(filename, index=False)
            print(f"✅ Saved {len(product_urls)} product URLs to {filename}")

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
        finally:
            driver.quit()

# Run steps
fetch_sitemap_links()
scrape_products_from_links()

all_urls = []

for file in os.listdir(products_folder):
    if file.endswith(".csv") and file.startswith("products_"):
        file_path = os.path.join(products_folder, file)
        df = pd.read_csv(file_path)
        all_urls.extend(df['Product URLs'].dropna().tolist())

# Remove duplicates
all_urls = list(set(all_urls))

# Save final merged CSV
pd.DataFrame({"Product URLs": all_urls}).to_csv(output_csv, index=False)
print(f"✅ Merged {len(all_urls)} unique product URLs into {output_csv}")
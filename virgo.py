import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# File paths
path_to_file = r"D:\Users\Asus\Python\job\shoppin\\"
output_html = os.path.join(path_to_file, "virgio_source.txt")
output_csv = os.path.join(path_to_file, "virgio_products.csv")

# Config
url = "https://www.virgio.com/collections/all"
scroll_pause = 6  # Delay between scrolls
scroll_step = 500  # px per scroll step
max_wait = 15  # Max times to retry if height doesn't change

# Set mode
mode = ""  # options: "", "scrape", "extract"

# Step 1: Scroll + Save Page Source
if mode != "extract":
    print("🚀 Starting browser and scrolling page slowly...")

    options = Options()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment for headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(2)

    last_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_scrolls = 0

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

    # Save HTML
    page_source = driver.page_source
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(page_source)

    driver.quit()
    print(f"📄 Page source saved to: {output_html}")

# Step 2: Parse HTML and extract product links
if mode != "scrape":
    print("🔍 Parsing saved HTML...")

    with open(output_html, "r", encoding="utf-8") as f:
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
    df.to_csv(output_csv, index=False)

    print(f"✅ Extracted {len(df)} product links")
    print(f"📁 Saved to: {output_csv}")

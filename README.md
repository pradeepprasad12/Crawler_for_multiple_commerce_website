This project scrapes product URLs from four major Indian fashion e-commerce websites: Virgio, Westside, TataCliq, and Nykaa Fashion. The scraper uses Selenium for dynamic scrolling and page interaction, and BeautifulSoup for parsing HTML to extract product links. Here's the breakdown of the approach per website:

1. Virgio
Target Page: https://www.virgio.com/collections/all

Approach:

Launch page using Selenium.

Scroll down repeatedly until no new content loads.

Save the full HTML page source.

Use BeautifulSoup to extract product URLs from anchor tags with data-discover="true".

Save extracted links to virgio_products.csv.

2. Westside
Target Page: https://www.westside.com/products/

Approach:

Load parent categories from the main collection list.

Visit each category link individually.

Scroll down incrementally until no new products are loaded.

Parse product links using BeautifulSoup by targeting anchor tags with class wizzy-result-product-item.

Save unique product URLs to westside_products.json.

3. TataCliq
Target Page: https://www.tatacliq.com/sitemap

Approach:

Extract subcategory links from the sitemap page.

For each subcategory, open the link and scroll/click “Show More Products” button repeatedly.

Parse product cards inside the grid container.

Extract all product links and save them category-wise in multiple CSVs.

Finally, merge all into a single file: tatacliq_all_products.csv.

4. Nykaa Fashion
Target Page: https://www.nykaafashion.com/cp/sitemap

Approach:

Scrape all subcategory links from the sitemap.

Visit each subcategory and scroll slowly to load more products.

Parse product URLs from anchor tags inside the main container with class css-bvydcl.

Detect the end of scrolling when product count stops increasing.

Save all unique links in nykaa_products.csv along with category info.

✅ Common Features
Uses Selenium for JavaScript-heavy pages.

Uses BeautifulSoup for HTML parsing and product link extraction.

Deduplicates all product URLs before saving.

Saves output in structured formats: CSV or JSON per website.

Modular functions for easy maintenance and extension.
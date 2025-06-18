# main.py

from reddit_scraper import fetch_post_data
from pdf_generator import generate_pdf

url = input("🔗 Enter the Reddit post URL: ")

print("🔄 Fetching Reddit post...")
post = fetch_post_data(url)

print("📦 Generating PDF...")
generate_pdf(post)

print("✅ Done! Check your folder for the PDF file.")

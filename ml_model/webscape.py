import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from io import BytesIO
import time

# Create a directory to store real medicine images
os.makedirs("real_medicines", exist_ok=True)

# Example search keywords (you can expand this)
medicine_keywords = ["paracetamol", "dolo", "azithromycin", "amoxicillin", "cetirizine"]

headers = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_images(query):
    print(f"Searching for: {query}")
    url = f"https://www.netmeds.com/catalogsearch/result?q={query}"
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        img_tags = soup.select("img.product-image-photo")

        count = 0
        for img in img_tags:
            src = img.get("src")
            if src and "https" in src:
                try:
                    img_data = requests.get(src).content
                    img_file = Image.open(BytesIO(img_data)).convert("RGB")
                    filename = f"real_medicines/{query}_{count}.jpg"
                    img_file.save(filename)
                    print(f"Saved: {filename}")
                    count += 1
                    time.sleep(1)  # be nice to the server
                except Exception as e:
                    print(f"Failed to save image: {e}")
                    
    except Exception as e:
        print(f"Error fetching {query}: {e}")

# Loop through the medicine keywords
for keyword in medicine_keywords:
    fetch_images(keyword)

print("✅ Done scraping real medicine images.")

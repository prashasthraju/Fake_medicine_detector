import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from io import BytesIO
import time
import random
import logging
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create directories if they don't exist
os.makedirs("real_medicines", exist_ok=True)
os.makedirs("fake_medicines", exist_ok=True)

# Medicine keywords for real medicines
real_medicine_keywords = [
    "paracetamol", "dolo", "azithromycin", "amoxicillin", "cetirizine",
    "omeprazole", "metformin", "atorvastatin", "aspirin", "ibuprofen"
]

# URLs for medicine images
medicine_urls = [
    "https://www.1mg.com/search/all?name={}",
    "https://pharmeasy.in/search/all?name={}",
    "https://www.netmeds.com/catalogsearch/result?q={}"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def download_image(url, save_path):
    """Download and save an image with error handling"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGB")
        
        # Resize if too large
        if max(img.size) > 1000:
            ratio = 1000 / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        img.save(save_path, "JPEG", quality=95)
        return True
    except Exception as e:
        logger.error(f"Error downloading image from {url}: {str(e)}")
        return False

def fetch_images_from_url(url_template, keyword, folder):
    """Fetch images from a specific URL template"""
    try:
        url = url_template.format(keyword)
        logger.info(f"Fetching from: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Different selectors for different websites
        img_selectors = [
            "img.product-image-photo",  # Netmeds
            "img[src*='medicine']",     # 1mg
            "img[src*='product']",      # Pharmeasy
            "img[alt*='medicine']",
            "img[alt*='tablet']",
            "img[alt*='capsule']"
        ]
        
        img_tags = []
        for selector in img_selectors:
            img_tags.extend(soup.select(selector))
        
        count = 0
        for img in img_tags:
            src = img.get("src") or img.get("data-src")
            if src and "http" in src:
                filename = f"{folder}/{keyword}_{count}.jpg"
                if download_image(src, filename):
                    logger.info(f"Saved: {filename}")
                    count += 1
                    time.sleep(random.uniform(1, 2))  # Random delay
                
                if count >= 5:  # Limit images per keyword
                    break
                    
    except Exception as e:
        logger.error(f"Error fetching from {url_template}: {str(e)}")

def generate_fake_medicine_images():
    """Generate fake medicine images by modifying real ones"""
    real_images = [f for f in os.listdir("real_medicines") if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    for i, real_img in enumerate(real_images[:10]):  # Generate 10 fake images
        try:
            # Load real image
            img_path = os.path.join("real_medicines", real_img)
            img = Image.open(img_path)
            
            # Apply random modifications
            if random.random() < 0.5:
                # Add noise
                img_array = np.array(img)
                noise = np.random.normal(0, 25, img_array.shape).astype(np.uint8)
                img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
                img = Image.fromarray(img_array)
            else:
                # Change colors
                img = img.convert('HSV')
                img_array = np.array(img)
                img_array[:,:,0] = (img_array[:,:,0] + random.randint(-30, 30)) % 180
                img = Image.fromarray(img_array).convert('RGB')
            
            # Save fake image
            fake_path = os.path.join("fake_medicines", f"fake_{i}.jpg")
            img.save(fake_path, "JPEG", quality=95)
            logger.info(f"Generated fake image: {fake_path}")
            
        except Exception as e:
            logger.error(f"Error generating fake image: {str(e)}")

def main():
    logger.info("Starting image collection...")
    
    # Collect real medicine images
    for keyword in real_medicine_keywords:
        logger.info(f"\nSearching for: {keyword}")
        for url_template in medicine_urls:
            fetch_images_from_url(url_template, keyword, "real_medicines")
            time.sleep(random.uniform(2, 3))  # Random delay between URLs
    
    # Generate fake medicine images
    logger.info("\nGenerating fake medicine images...")
    generate_fake_medicine_images()
    
    # Print summary
    real_count = len([f for f in os.listdir("real_medicines") if f.endswith(('.jpg', '.jpeg', '.png'))])
    fake_count = len([f for f in os.listdir("fake_medicines") if f.endswith(('.jpg', '.jpeg', '.png'))])
    
    logger.info(f"\n✅ Collection complete!")
    logger.info(f"Real medicine images: {real_count}")
    logger.info(f"Fake medicine images: {fake_count}")

if __name__ == "__main__":
    main()

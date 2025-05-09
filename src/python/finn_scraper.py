
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import random
from PIL import Image
from io import BytesIO
import os
import pickle
import re
from urllib.parse import urljoin

class FinnScraper:
    def __init__(self, base_url="https://www.finn.no/mobility/search/car?registration_class=1"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.data = pd.DataFrame(columns=['finn_id', 'title', 'brand', 'model', 'year', 'price', 'location', 'url', 'image_urls'])
        self.images = {}  # Dictionary to store images as numpy arrays
        
    def scrape_listings(self, pages=2):
        """Scrape multiple pages of car listings"""
        all_listings = []
        
        for page in range(1, pages + 1):
            url = f"{self.base_url}&page={page}"
            print(f"Scraping page {page}...")
            
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = soup.select('article.sf-search-unit')
            
            for listing in listings:
                try:
                    # Extract listing URL and ID
                    link_elem = listing.select_one('a.sf-search-unit__link')
                    if not link_elem:
                        continue
                        
                    listing_url = urljoin("https://www.finn.no", link_elem['href'])
                    finn_id = re.search(r'/(\d+)$', listing_url)
                    if not finn_id:
                        continue
                    finn_id = finn_id.group(1)
                    
                    # Extract title which contains brand and model
                    title_elem = listing.select_one('.sf-search-unit__title')
                    title = title_elem.text.strip() if title_elem else "Unknown"
                    
                    # Try to extract brand and model from title
                    brand = "Unknown"
                    model = "Unknown"
                    if title != "Unknown":
                        title_parts = title.split()
                        if len(title_parts) > 0:
                            brand = title_parts[0]
                            model = ' '.join(title_parts[1:2]) if len(title_parts) > 1 else ""
                    
                    # Extract price
                    price_elem = listing.select_one('.sf-search-unit__price')
                    price = price_elem.text.strip() if price_elem else "Unknown"
                    price = re.sub(r'[^\d]', '', price) if price != "Unknown" else 0
                    
                    # Extract location
                    location_elem = listing.select_one('.sf-search-unit__location')
                    location = location_elem.text.strip() if location_elem else "Unknown"
                    
                    # Extract year if available
                    year_elem = listing.select_one('.sf-search-unit__subtitle')
                    year = "Unknown"
                    if year_elem:
                        year_match = re.search(r'(\d{4})', year_elem.text)
                        if year_match:
                            year = year_match.group(1)
                    
                    # Extract image URL
                    image_elem = listing.select_one('img.responsive-image')
                    image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else None
                    
                    all_listings.append({
                        'finn_id': finn_id,
                        'title': title,
                        'brand': brand,
                        'model': model,
                        'year': year,
                        'price': price,
                        'location': location,
                        'url': listing_url,
                        'image_urls': [image_url] if image_url else []
                    })
                    
                except Exception as e:
                    print(f"Error processing listing: {e}")
            
            # Add delay between requests to be respectful to the server
            time.sleep(random.uniform(1, 3))
            
        # Convert to DataFrame
        self.data = pd.DataFrame(all_listings)
        return self.data
    
    def scrape_listing_details(self, sample_size=None):
        """Scrape details from individual listing pages"""
        if self.data.empty:
            print("No listings to process. Run scrape_listings() first.")
            return
        
        # Process either all listings or a sample
        listings_to_process = self.data.sample(sample_size) if sample_size else self.data
        
        for idx, listing in listings_to_process.iterrows():
            try:
                print(f"Scraping details for listing {listing['finn_id']}...")
                
                response = requests.get(listing['url'], headers=self.headers)
                if response.status_code != 200:
                    print(f"Failed to fetch listing {listing['finn_id']}")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get all image URLs
                image_elements = soup.select('img.u-border-radius-0')
                image_urls = [img['src'] for img in image_elements if 'src' in img.attrs]
                
                # Update the DataFrame with image URLs
                self.data.at[idx, 'image_urls'] = image_urls
                
                # Download images and store as numpy arrays (only first 5 images to save memory)
                images_array = []
                for i, img_url in enumerate(image_urls[:5]):
                    try:
                        img_response = requests.get(img_url, headers=self.headers)
                        img = Image.open(BytesIO(img_response.content))
                        img_array = np.array(img)
                        images_array.append(img_array)
                    except Exception as e:
                        print(f"Error downloading image {i} for listing {listing['finn_id']}: {e}")
                
                # Store images in the dictionary
                if images_array:
                    self.images[listing['finn_id']] = images_array
                
                # Be respectful to the server
                time.sleep(random.uniform(1.5, 3.5))
                
            except Exception as e:
                print(f"Error processing listing details for {listing['finn_id']}: {e}")
    
    def save_data(self, data_file='finn_cars.pkl', images_file='finn_car_images.npz'):
        """Save the scraped data to files"""
        # Save DataFrame
        self.data.to_pickle(data_file)
        print(f"Data saved to {data_file}")
        
        # Save images
        np.savez_compressed(images_file, **{str(k): np.array(v) for k, v in self.images.items()})
        print(f"Images saved to {images_file}")
    
    def load_data(self, data_file='finn_cars.pkl', images_file='finn_car_images.npz'):
        """Load previously saved data"""
        if os.path.exists(data_file):
            self.data = pd.read_pickle(data_file)
            print(f"Data loaded from {data_file}")
        
        if os.path.exists(images_file):
            loaded = np.load(images_file, allow_pickle=True)
            self.images = {int(k): v for k, v in loaded.items()}
            print(f"Images loaded from {images_file}")
    
    def search_by_model(self, query):
        """Search for cars by brand and model"""
        query = query.lower()
        
        # Search in brand and model columns
        brand_matches = self.data[self.data['brand'].str.lower().str.contains(query)]
        model_matches = self.data[self.data['model'].str.lower().str.contains(query)]
        title_matches = self.data[self.data['title'].str.lower().str.contains(query)]
        
        # Combine all matches and drop duplicates
        all_matches = pd.concat([brand_matches, model_matches, title_matches])
        return all_matches.drop_duplicates(subset=['finn_id'])

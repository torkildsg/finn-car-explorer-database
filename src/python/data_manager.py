
import os
import json
import pandas as pd
import numpy as np
from finn_scraper import FinnScraper

class DataManager:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, 'finn_cars.pkl')
        self.images_file = os.path.join(data_dir, 'finn_car_images.npz')
        self.scraper = FinnScraper()
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data if available
        if os.path.exists(self.data_file):
            self.load_data()
        else:
            self.data = pd.DataFrame()
            self.images = {}
    
    def scrape_data(self, pages=5, sample_details=20):
        """Scrape data from Finn.no"""
        print("Starting data scraping...")
        
        # Scrape listings
        self.scraper.scrape_listings(pages=pages)
        
        # Scrape details for a sample of listings to avoid overloading
        self.scraper.scrape_listing_details(sample_size=sample_details)
        
        # Save the scraped data
        self.scraper.save_data(self.data_file, self.images_file)
        
        # Update our local copy
        self.data = self.scraper.data
        self.images = self.scraper.images
        
        print(f"Scraping complete. {len(self.data)} listings collected.")
    
    def load_data(self):
        """Load data from saved files"""
        self.scraper.load_data(self.data_file, self.images_file)
        self.data = self.scraper.data
        self.images = self.scraper.images
        print(f"Data loaded. {len(self.data)} listings available.")
    
    def search(self, query):
        """Search for cars by brand/model"""
        if self.data.empty:
            self.load_data()
            
        results = self.scraper.search_by_model(query)
        return results
    
    def get_search_results_json(self, query):
        """Get search results as JSON for the web interface"""
        results = self.search(query)
        
        if results.empty:
            return json.dumps([])
        
        # Format results for the frontend
        formatted_results = []
        for _, row in results.iterrows():
            formatted_results.append({
                'finn_id': row['finn_id'],
                'title': row['title'],
                'brand': row['brand'],
                'model': row['model'],
                'year': row['year'],
                'price': f"{int(row['price']):,} kr" if row['price'] != 'Unknown' and row['price'] != 0 else "Unknown",
                'location': row['location'],
                'url': row['url'],
                'image_url': row['image_urls'][0] if row['image_urls'] and len(row['image_urls']) > 0 else None
            })
        
        return json.dumps(formatted_results)
    
    def get_data_summary(self):
        """Get summary statistics of the dataset"""
        if self.data.empty:
            self.load_data()
        
        if self.data.empty:
            return {
                'total_listings': 0,
                'brands': [],
                'price_range': [0, 0],
                'years_range': [0, 0]
            }
        
        summary = {
            'total_listings': len(self.data),
            'brands': self.data['brand'].value_counts().to_dict(),
            'price_range': [
                int(self.data['price'].astype(float).min()) if not self.data['price'].empty else 0,
                int(self.data['price'].astype(float).max()) if not self.data['price'].empty else 0
            ],
            'years_range': [
                int(min([int(y) for y in self.data['year'] if y != 'Unknown' and y.isdigit()])) if not self.data['year'].empty else 0,
                int(max([int(y) for y in self.data['year'] if y != 'Unknown' and y.isdigit()])) if not self.data['year'].empty else 0
            ]
        }
        
        return summary


# Finn.no Car Scraper and Database

This Python package scrapes car listings from Finn.no, processes and structures the data, and provides a dataset for machine learning applications.

## Requirements

- Python 3.8+
- Required packages:
  - pandas
  - numpy
  - requests
  - beautifulsoup4
  - pillow
  - torch

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Scraping Data

```python
from finn_scraper import FinnScraper

# Initialize scraper
scraper = FinnScraper()

# Scrape listings (first 5 pages)
scraper.scrape_listings(pages=5)

# Get details for scraped listings (first 20 listings)
scraper.scrape_listing_details(sample_size=20)

# Save data
scraper.save_data()
```

### Using the Dataset

```python
import torch
from car_dataset import FinnCarDataset
from torchvision import transforms

# Define transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load dataset
dataset = FinnCarDataset(transform=transform)

# Create DataLoader
dataloader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)

# Use in your model
for batch in dataloader:
    images = batch['image']
    brands = batch['brand']
    # ... use in your model
```

### Search Operations

```python
from data_manager import DataManager

# Initialize data manager
dm = DataManager()

# Load existing data or scrape new data
dm.load_data()  # or dm.scrape_data() to get fresh data

# Search for cars
results = dm.search("audi a3")
print(f"Found {len(results)} matching cars")
```

## Ethical Considerations

- This scraper should be used responsibly and in accordance with Finn.no's terms of service
- Include delays between requests to avoid overloading the server
- Consider implementing a user agent rotation if doing extensive scraping

## Data Structure

The data is stored in two formats:
1. A pandas DataFrame (`finn_cars.pkl`) containing metadata
2. A NumPy compressed file (`finn_car_images.npz`) containing image arrays

## Machine Learning Applications

The `FinnCarDataset` class is designed to be used with PyTorch models for:
- Car condition classification
- Price prediction
- Brand/model classification

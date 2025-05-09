
import torch
from torch.utils.data import Dataset
import numpy as np
import pandas as pd
from PIL import Image
import os

class FinnCarDataset(Dataset):
    def __init__(self, data_file='finn_cars.pkl', images_file='finn_car_images.npz', transform=None):
        """
        Custom PyTorch Dataset for Finn.no car listings
        
        Args:
            data_file: Path to the pickled DataFrame with car metadata
            images_file: Path to the NPZ file containing image arrays
            transform: Optional transform to be applied to the images
        """
        self.transform = transform
        
        # Load data
        if os.path.exists(data_file):
            self.data = pd.read_pickle(data_file)
        else:
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        # Load images
        if os.path.exists(images_file):
            self.images_data = np.load(images_file, allow_pickle=True)
            self.finn_ids = [int(id) for id in self.images_data.files]
            
            # Filter data to only include entries with images
            self.data = self.data[self.data['finn_id'].astype(str).isin(self.images_data.files)]
        else:
            raise FileNotFoundError(f"Images file not found: {images_file}")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        
        # Get metadata
        row = self.data.iloc[idx]
        finn_id = str(row['finn_id'])
        
        # Get images (first image in the array)
        if finn_id in self.images_data.files:
            # Get the first image in the array
            img_array = self.images_data[finn_id][0] if isinstance(self.images_data[finn_id], np.ndarray) and len(self.images_data[finn_id]) > 0 else None
            
            if img_array is not None:
                # Convert numpy array to PIL Image
                img = Image.fromarray(img_array)
                
                # Apply transformations if any
                if self.transform:
                    img = self.transform(img)
            else:
                # Create a dummy tensor if no image is available
                img = torch.zeros((3, 224, 224))
        else:
            # Create a dummy tensor if finn_id not in images
            img = torch.zeros((3, 224, 224))
        
        # Create a sample with metadata and image
        sample = {
            'finn_id': row['finn_id'],
            'brand': row['brand'],
            'model': row['model'],
            'year': row['year'],
            'price': float(row['price']) if isinstance(row['price'], (int, str)) and row['price'] != 'Unknown' else 0.0,
            'image': img
        }
        
        return sample
    
    def get_all_images_for_id(self, finn_id):
        """Get all available images for a specific finn_id"""
        finn_id_str = str(finn_id)
        if finn_id_str in self.images_data.files:
            img_arrays = self.images_data[finn_id_str]
            images = []
            
            for img_array in img_arrays:
                img = Image.fromarray(img_array)
                if self.transform:
                    img = self.transform(img)
                images.append(img)
            
            return images
        
        return None

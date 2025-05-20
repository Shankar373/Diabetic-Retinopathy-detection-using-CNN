import torch
from torch.utils.data import Dataset
import pandas as pd
import cv2
import numpy as np
from pathlib import Path
from .preprocess import create_augmentation_pipeline

class DRDataset(Dataset):
    """
    Dataset class for Diabetic Retinopathy Detection.
    """
    def __init__(self, csv_file, img_dir, train=True):
        """
        Args:
            csv_file (str): Path to labels CSV file
            img_dir (str): Directory with images
            train (bool): If True, creates dataset from training set
        """
        self.data = pd.read_csv(csv_file)
        self.img_dir = Path(img_dir)
        self.train = train
        self.transform = create_augmentation_pipeline(training=train)
        
        # Calculate class weights for balanced sampling
        if train:
            self.class_weights = self._calculate_class_weights()
            labels = self.data['label'].values
            self.sample_weights = [self.class_weights[int(label)] for label in labels]
    
    def _calculate_class_weights(self):
        """Calculate class weights for balanced sampling."""
        class_counts = self.data['label'].value_counts()
        total = len(self.data)
        class_weights = {int(cls): total / (len(class_counts) * count) 
                        for cls, count in class_counts.items()}
        return class_weights
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
            
        # Get image path
        img_name = self.data.iloc[idx]['filename']
        img_path = self.img_dir / img_name
        
        # Read and preprocess image
        image = cv2.imread(str(img_path))
        if image is None:
            raise ValueError(f"Failed to load image: {img_path}")
            
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply augmentations
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented['image']
            
        # Get label
        label = self.data.iloc[idx]['label']
        label = torch.tensor(label, dtype=torch.long)
        
        return image, label

def create_datasets(train_csv, val_csv, train_dir, val_dir):
    """
    Create train and validation datasets.
    
    Args:
        train_csv (str): Path to training labels CSV
        val_csv (str): Path to validation labels CSV
        train_dir (str): Directory with training images
        val_dir (str): Directory with validation images
        
    Returns:
        tuple: Training and validation datasets
    """
    train_dataset = DRDataset(
        csv_file=train_csv,
        img_dir=train_dir,
        train=True
    )
    
    val_dataset = DRDataset(
        csv_file=val_csv,
        img_dir=val_dir,
        train=False
    )
    
    return train_dataset, val_dataset

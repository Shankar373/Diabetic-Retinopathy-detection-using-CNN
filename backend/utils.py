import torch
from torchvision import transforms
from pathlib import Path
from PIL import Image
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DRDataGenerator(torch.utils.data.Dataset):
    def __init__(self, data_dir, training=True, target_size=(224, 224)):
        logger.info(f"Initializing DRDataGenerator with data_dir: {data_dir}")
        self.data_dir = Path(data_dir)
        self.training = training
        self.target_size = target_size

        # Load and validate labels
        try:
            labels_df = pd.read_csv(self.data_dir / 'labels.csv')
            logger.info(f"Loaded labels_df: {labels_df.head()}")
            
            # Validate label values are in range [0-4]
            if not all(labels_df['label'].between(0, 4)):
                raise ValueError("Labels must be in range [0-4]")
                
            labels_dict = dict(zip(labels_df['filename'], labels_df['label']))
        except FileNotFoundError:
            raise FileNotFoundError(f"Labels file not found at {self.data_dir / 'labels.csv'}")
        except Exception as e:
            raise ValueError(f"Error loading labels: {str(e)}")

        # Get all image paths and their corresponding labels
        self.image_paths = []
        self.labels = []
        
        # Get all JPEG files and sort them for consistency
        jpeg_files = sorted(self.data_dir.glob('**/*.jpeg'))
        
        for img_path in jpeg_files:
            try:
                relative_path = img_path.name  # Using just filename instead of relative path
                if relative_path in labels_dict:
                    # Verify the image can be opened
                    with Image.open(img_path) as img:
                        if img.mode not in ['RGB', 'L']:
                            logger.warning(f"Skipping {relative_path} - unsupported image mode: {img.mode}")
                            continue
                    
                    self.image_paths.append(img_path)
                    self.labels.append(labels_dict[relative_path])
                    logger.info(f"Added image {relative_path} with label {labels_dict[relative_path]}")
                else:
                    logger.warning(f"Skipping {relative_path} - no label found")
            except Exception as e:
                logger.warning(f"Error processing {img_path}: {str(e)}")
                continue

        if not self.image_paths:
            raise ValueError("No valid images found with corresponding labels")

        # Log dataset statistics
        logger.info(f"Found {len(self.image_paths)} valid images")
        label_dist = pd.Series(self.labels).value_counts().sort_index()
        logger.info(f"Label distribution:\n{label_dist}")

        # Set up image transformations
        if self.training:
            self.transform = transforms.Compose([
                transforms.Resize(self.target_size),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomRotation(10),
                transforms.ColorJitter(brightness=0.2, contrast=0.2),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                  std=[0.229, 0.224, 0.225])
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize(self.target_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                  std=[0.229, 0.224, 0.225])
            ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        try:
            if idx >= len(self.image_paths):
                raise IndexError(f"Index {idx} out of bounds for dataset of size {len(self.image_paths)}")
                
            img_path = self.image_paths[idx]
            label = self.labels[idx]
            
            # Load and process image
            with Image.open(img_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                image = self.transform(img)
            
            return image, label
            
        except Exception as e:
            logger.error(f"Error accessing index {idx}: {str(e)}")
            raise  # Re-raise the exception after logging

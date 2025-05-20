import torch  # Add PyTorch import if not present
from torchvision import transforms
from pathlib import Path
from PIL import Image

import logging

class DRDataGenerator(torch.utils.data.Dataset):
    def __init__(self, data_dir, training=True, batch_size=32, target_size=(224, 224)):
        self.data_dir = Path(data_dir)
        self.training = training
        self.target_size = target_size
        self.transform = transforms.Compose([
            transforms.Resize(self.target_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

        # Log the search path
        logging.info(f"Searching for images in: {self.data_dir}")

        # Create a list with image paths and labels
        self.image_paths = list(self.data_dir.glob('**/*.jpeg'))
        self.labels = [self.get_label(img_path) for img_path in self.image_paths]  # Adjust as needed

        # Log the number of images and labels
        logging.info(f"Number of images found: {len(self.image_paths)}")
        logging.info(f"Number of labels found: {len(self.labels)}")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        try:
            image = Image.open(img_path).convert('RGB')
            image = self.transform(image)
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            return None, None
        label = self.labels[idx]
        return image, label

def get_label(self, img_path):
    # Extract label from the filename
    # Assuming filenames are in the format 'ID_label.jpeg'
    filename = img_path.stem
    label = int(filename.split('_')[1])
    return label

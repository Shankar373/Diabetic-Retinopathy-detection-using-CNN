import os
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_sample_image(size=(224, 224)):
    """Generate a random sample image with realistic features"""
    np.random.seed(42)  # For reproducibility
    
    # Create base image
    base = np.random.randint(100, 200, size=(*size, 3), dtype=np.uint8)
    
    # Add retinal features
    center_x, center_y = size[0] // 2, size[1] // 2
    y, x = np.ogrid[:size[0], :size[1]]
    dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    
    # Create circular mask
    mask = dist_from_center <= min(size) // 3
    base[mask] = np.random.randint(50, 150, size=3, dtype=np.uint8)
    
    # Add random spots
    for _ in range(10):
        spot_x = np.random.randint(0, size[0])
        spot_y = np.random.randint(0, size[1])
        spot_r = np.random.randint(5, 20)
        spot_mask = ((x - spot_x)**2 + (y - spot_y)**2) <= spot_r**2
        base[spot_mask] = np.random.randint(0, 255, size=3, dtype=np.uint8)
    
    return base

def setup_directory_structure():
    """Create the directory structure for dataset"""
    base_dir = Path(__file__).parent
    directories = {
        'raw': base_dir / 'data' / 'raw',
        'processed': base_dir / 'data' / 'processed',
        'train': base_dir / 'data' / 'processed' / 'train',
        'val': base_dir / 'data' / 'processed' / 'val',
    }
    
    # Create directories for each DR level
    for dir_path in directories.values():
        dir_path.mkdir(parents=True, exist_ok=True)
        if 'processed' in str(dir_path):
            for i in range(5):  # 5 DR levels
                (dir_path / str(i)).mkdir(exist_ok=True)
    
    return directories

def create_sample_data(directories):
    """Create sample data for testing"""
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate sample images for each class
    for dr_level in range(5):
        train_dir = directories['train'] / str(dr_level)
        val_dir = directories['val'] / str(dr_level)
        
        # Create sample images
        for i in range(10):  # 10 samples per class
            # Generate random image
            img_array = generate_sample_image()
            img = Image.fromarray(img_array)
            
            # Save to train and validation directories
            if i < 8:  # 80% train
                img.save(train_dir / f'sample_{i}.jpg')
            else:  # 20% validation
                img.save(val_dir / f'sample_{i}.jpg')

def main():
    try:
        logger.info("Setting up directory structure...")
        directories = setup_directory_structure()
        
        logger.info("Creating sample data...")
        create_sample_data(directories)
        
        logger.info("Data preparation completed!")
        logger.info(f"Data directory structure created at: {directories['raw'].parent}")
    except Exception as e:
        logger.error(f"Error during data preparation: {str(e)}")
        raise

if __name__ == "__main__":
    main()

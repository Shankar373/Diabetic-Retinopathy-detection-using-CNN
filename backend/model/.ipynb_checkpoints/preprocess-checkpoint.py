import os
import argparse
import cv2
import numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import albumentations as A
from albumentations.pytorch import ToTensorV2

def create_augmentation_pipeline(training=True):
    if training:
        return A.Compose([
            A.RandomRotate90(p=0.5),
            A.Flip(p=0.5),
            A.OneOf([
                A.RandomBrightness(limit=0.2, p=1),
                A.RandomContrast(limit=0.2, p=1),
                A.RandomGamma(p=1)
            ], p=0.5),
            A.OneOf([
                A.GaussNoise(p=1),
                A.MedianBlur(blur_limit=3, p=1),
                A.GaussianBlur(blur_limit=3, p=1)
            ], p=0.2),
            A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.5),
            A.HueSaturationValue(p=0.3),
            A.RandomCrop(height=224, width=224, p=0.5),
            A.RandomResizedCrop(height=224, width=224, scale=(0.8, 1.0), p=0.5),
            ToTensorV2(),
        ])
    else:
        return A.Compose([
            A.Resize(height=224, width=224),
            ToTensorV2(),
        ])

def preprocess_single_image(args, training=False):
    """
    Preprocess a single image.

    Args:
        args (tuple): Tuple containing image path, output directory, and augmentation flag.
        training (bool): Flag indicating if the image is for training.

    Returns:
        bool: True if preprocessing was successful, False otherwise.
    """
    img_path, output_dir, do_augment = args
    try:
        # Read image
        img = cv2.imread(str(img_path))
        if img is None:
            return False

        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Basic preprocessing
        img = cv2.resize(img, (224, 224))

        # Save original
        out_path = Path(output_dir) / img_path.name
        cv2.imwrite(str(out_path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

        # Augmentation if requested and training
        if do_augment and training:
            transform = create_augmentation_pipeline(training=True)
            for i in range(3):
                augmented = transform(image=img)['image']
                aug_path = Path(output_dir) / f"aug_{i}_{img_path.name}"
                cv2.imwrite(str(aug_path), cv2.cvtColor(augmented, cv2.COLOR_RGB2BGR))

        return True
    except Exception as e:
        print(f"Error processing {img_path}: {str(e)}")
        return False

def preprocess_images(input_dir, output_dir, do_augment=True, n_workers=4):
    """
    Preprocess images in parallel.

    Args:
        input_dir (str): Directory containing input images.
        output_dir (str): Directory to save preprocessed images.
        do_augment (bool): Flag indicating if augmentations should be applied.
        n_workers (int): Number of worker processes for parallel processing.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get list of all images
    image_paths = [
        p for p in input_dir.glob("**/*")
        if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}
    ]

    # Create arguments for parallel processing
    process_args = [(p, output_dir, do_augment) for p in image_paths]

    # Process images in parallel
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        results = list(tqdm(
            executor.map(preprocess_single_image, process_args),
            total=len(process_args),
            desc="Preprocessing images"
        ))

    # Print statistics
    successful = sum(results)
    print(f"\nProcessed {successful}/{len(image_paths)} images successfully")
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--no-augment', action='store_true')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    
    preprocess_images(
        args.input_dir, 
        args.output_dir, 
        do_augment=not args.no_augment,
        n_workers=args.workers
    )

if __name__ == '__main__':
    main()

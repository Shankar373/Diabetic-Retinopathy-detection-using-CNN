import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
import pandas as pd
import numpy as np
from pathlib import Path
import cv2
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import argparse
from PIL import Image

class DRDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform or transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        return image, label

def create_model(num_classes=5):
    model = models.resnet50(pretrained=True)
    # Modify the final layer for our classification task
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

def train_model(model, train_loader, val_loader, device, epochs=50, lr=1e-4):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5)
    
    best_val_acc = 0.0
    for epoch in range(epochs):
        # Training phase
        model.train()
        running_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for inputs, labels in tqdm(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        train_acc = 100. * train_correct / train_total
        val_acc = 100. * val_correct / val_total
        
        print(f'Epoch [{epoch+1}/{epochs}] Train Loss: {running_loss/len(train_loader):.4f} '
              f'Train Acc: {train_acc:.2f}% Val Loss: {val_loss/len(val_loader):.4f} '
              f'Val Acc: {val_acc:.2f}%')

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), 'best_model.pth')
        
        scheduler.step(val_loss)

def preprocess_data(data_dir: Path):
    """
    Preprocess data by reading the CSV file and splitting it into training and validation sets.

    Args:
        data_dir (Path): Path to the dataset directory.

    Returns:
        tuple: Training and validation image paths and labels.
    """
    df = pd.read_csv(data_dir / 'trainLabels.csv')
    image_paths = [(data_dir / 'train' / f"{id}.jpeg") for id in df['image']]
    labels = df['level'].values

    return train_test_split(
        image_paths, labels,
        test_size=0.2,
        stratify=labels,
        random_state=42
    )

def main(data_dir: Path, epochs=50, batch_size=32):
    """
    Main function to prepare data, create model, and train it.

    Args:
        data_dir (Path): Path to the dataset directory.
        epochs (int): Number of epochs to train.
        batch_size (int): Batch size for training.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Prepare data
    train_paths, val_paths, train_labels, val_labels = preprocess_data(data_dir)

    # Create datasets
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    train_dataset = DRDataset(train_paths, train_labels, transform=train_transform)
    val_dataset = DRDataset(val_paths, val_labels, transform=val_transform)

    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)

    # Create and train model
    model = create_model()
    model = model.to(device)
    train_model(model, train_loader, val_loader, device, epochs=epochs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train DR detection model')
    parser.add_argument('--data-dir', type=str, required=True,
                      help='Path to dataset directory')
    parser.add_argument('--epochs', type=int, default=50,
                      help='Number of epochs to train')
    parser.add_argument('--batch-size', type=int, default=32,
                      help='Batch size for training')

    args = parser.parse_args()
    main(Path(args.data_dir), epochs=args.epochs, batch_size=args.batch_size)

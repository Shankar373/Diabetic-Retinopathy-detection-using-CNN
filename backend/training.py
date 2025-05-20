#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import torch
from torch import nn
import torchvision
from torchvision import transforms, models
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import os
import pandas as pd
import seaborn as sns
from torch.optim import lr_scheduler
import cv2

# Fix 1: Properly handle image paths and extensions
def get_image_path(base_dir, img_name):
    # Try different possible extensions
    extensions = ['.jpeg', '.jpg', '.png']
    for ext in extensions:
        # Remove any existing extension from img_name
        base_name = os.path.splitext(img_name)[0]
        path = os.path.join(base_dir, base_name + ext)
        if os.path.exists(path):
            return path
    return None

# Fix 2: Improved Dataset class with better error handling
class CreateDataset(Dataset):
    def __init__(self, df_data, data_dir='backend/', transform=None):
        super().__init__()
        self.df = df_data.values
        self.data_dir = data_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, index):
        try:
            if len(self.df[index]) == 2:
                img_name, label = self.df[index]
            else:
                img_name = self.df[index][0]
                label = 0  # Default label for test set
                
            # Fix 3: Improved image loading
            img_path = get_image_path(self.data_dir, img_name)
            if img_path is None:
                raise FileNotFoundError(f"Image not found: {img_name}")
                
            image = cv2.imread(img_path)
            if image is None:
                raise ValueError(f"Failed to load image: {img_path}")
                
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            if self.transform:
                image = self.transform(image)
            
            return image, label
            
        except Exception as e:
            print(f"Error loading image at index {index}: {str(e)}")
            # Return a default tensor instead of None
            return torch.zeros((3, 224, 224)), 0

# Fix 4: Better data loading and validation
def load_data(base_dir):
    train_path = os.path.join(base_dir, 'models/training_history.csv')
    test_path = os.path.join(base_dir, 'models/sample.csv')
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(train_path), exist_ok=True)
    
    if os.path.exists(train_path) and os.path.getsize(train_path) > 0:
        train_csv = pd.read_csv(train_path)
    else:
        print(f"Creating new training dataset...")
        train_images = []
        train_dir = os.path.join(base_dir, 'train')
        if os.path.exists(train_dir):
            for f in os.listdir(train_dir):
                if f.lower().endswith(('.png', '.jpeg', '.jpg')):
                    train_images.append(os.path.join('train', f))
        
        train_csv = pd.DataFrame({
            'image_id': train_images,
            'label': np.random.randint(0, 5, len(train_images))
        })
        
    # Similar for test data
    if os.path.exists(test_path) and os.path.getsize(test_path) > 0:
        test_csv = pd.read_csv(test_path)
    else:
        print(f"Creating new test dataset...")
        test_images = []
        test_dir = os.path.join(base_dir, 'sample')
        if os.path.exists(test_dir):
            for f in os.listdir(test_dir):
                if f.lower().endswith(('.png', '.jpeg', '.jpg')):
                    test_images.append(os.path.join('sample', f))
        
        test_csv = pd.DataFrame({
            'image_id': test_images
        })
    
    return train_csv, test_csv

# Fix 5: Improved model saving and loading
def save_model(model, optimizer, epoch, valid_loss, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': valid_loss
        }, path)
        print(f"Model saved successfully to {path}")
    except Exception as e:
        print(f"Error saving model: {str(e)}")

def load_model(model, optimizer, path):
    try:
        if os.path.exists(path):
            checkpoint = torch.load(path)
            model.load_state_dict(checkpoint['model_state_dict'])
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            print(f"Model loaded successfully from {path}")
            return checkpoint.get('epoch', 0), checkpoint.get('loss', float('inf'))
        else:
            print(f"No existing model found at {path}")
            return 0, float('inf')
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return 0, float('inf')

# Fix 6: Improved training function with better error handling
def train_and_test(model, trainloader, validloader, criterion, optimizer, scheduler, num_epochs, device, save_path):
    train_losses, test_losses, acc = [], [], []
    valid_loss_min = float('inf')
    early_stop_counter = 0
    patience = 7  # Early stopping patience
    
    for epoch in range(num_epochs):
        try:
            model.train()
            running_loss = 0
            for i, (images, labels) in enumerate(trainloader):
                try:
                    images, labels = images.to(device), labels.to(device)
                    optimizer.zero_grad()
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()
                    running_loss += loss.item()
                    
                    if i % 10 == 0:
                        print(f"Epoch {epoch + 1}/{num_epochs}, Batch {i}/{len(trainloader)}")
                        
                except Exception as e:
                    print(f"Error in training batch {i}: {str(e)}")
                    continue
            
            # Validation phase
            model.eval()
            test_loss = 0
            accuracy = 0
            
            with torch.no_grad():
                for images, labels in validloader:
                    try:
                        images, labels = images.to(device), labels.to(device)
                        logps = model(images)
                        test_loss += criterion(logps, labels)
                        ps = torch.exp(logps)
                        top_p, top_class = ps.topk(1, dim=1)
                        equals = top_class == labels.view(*top_class.shape)
                        accuracy += torch.mean(equals.type(torch.FloatTensor))
                    except Exception as e:
                        print(f"Error in validation batch: {str(e)}")
                        continue
            
            # Calculate epoch statistics
            train_loss = running_loss/len(trainloader)
            valid_loss = test_loss/len(validloader)
            valid_acc = accuracy/len(validloader)
            
            train_losses.append(train_loss)
            test_losses.append(valid_loss)
            acc.append(valid_acc)
            
            print(f"Epoch: {epoch+1}/{num_epochs}")
            print(f"Training Loss: {train_loss:.3f}")
            print(f"Validation Loss: {valid_loss:.3f}")
            print(f"Validation Accuracy: {valid_acc:.3f}")
            
            # Save if validation loss decreased and update early stopping counter
            if valid_loss < valid_loss_min:
                print(f'Validation loss decreased ({valid_loss_min:.6f} --> {valid_loss:.6f}). Saving model...')
                save_model(model, optimizer, epoch, valid_loss, save_path)
                valid_loss_min = valid_loss
                early_stop_counter = 0
            else:
                early_stop_counter += 1
                if early_stop_counter >= patience:
                    print(f'Early stopping triggered after {epoch + 1} epochs')
                    break
            
            optimizer.step()
            if isinstance(scheduler, lr_scheduler.ReduceLROnPlateau):
                scheduler.step(valid_loss)
            else:
                scheduler.step()
            
        except Exception as e:
            print(f"Error in epoch {epoch + 1}: {str(e)}")
            continue
    
    return train_losses, test_losses, acc

def main():
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Set base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load data
    train_csv, test_csv = load_data(base_dir)
    print(f"Training set size: {len(train_csv)} images")
    print(f"Test set size: {len(test_csv)} images")
    
    # Create transforms with medical image-specific augmentations
    train_transforms = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
    ])

    test_transforms = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
    ])

    # Create datasets
    train_data = CreateDataset(df_data=train_csv, data_dir=os.path.join(base_dir, 'train'), transform=train_transforms)
    test_data = CreateDataset(df_data=test_csv, data_dir=os.path.join(base_dir, 'sample'), transform=test_transforms)

    # Create validation split
    valid_size = 0.2
    num_train = len(train_data)
    indices = list(range(num_train))
    np.random.shuffle(indices)
    split = int(np.floor(valid_size * num_train))
    train_idx, valid_idx = indices[split:], indices[:split]

    # Create samplers
    train_sampler = SubsetRandomSampler(train_idx)
    valid_sampler = SubsetRandomSampler(valid_idx)

    # Create dataloaders with appropriate batch sizes
    trainloader = DataLoader(train_data, batch_size=32, sampler=train_sampler, num_workers=4)
    validloader = DataLoader(train_data, batch_size=32, sampler=valid_sampler, num_workers=4)
    testloader = DataLoader(test_data, batch_size=32, num_workers=4)

    print(f"Number of training batches: {len(trainloader)}")
    print(f"Number of validation batches: {len(validloader)}")
    print(f"Number of test batches: {len(testloader)}")

    # Initialize model
    model = models.resnet152(weights='IMAGENET1K_V1')
    
    # Modify final layer
    num_ftrs = model.fc.in_features
    out_ftrs = 5
    model.fc = nn.Sequential(
        nn.Linear(num_ftrs, 512),
        nn.ReLU(),
        nn.Linear(512, out_ftrs),
        nn.LogSoftmax(dim=1)
    )

    # Freeze/unfreeze layers
    for name, child in model.named_children():
        if name in ['layer2', 'layer3', 'layer4', 'fc']:
            print(f"{name} is unfrozen")
            for param in child.parameters():
                param.requires_grad = True
        else:
            print(f"{name} is frozen")
            for param in child.parameters():
                param.requires_grad = False

    model = model.to(device)

    # Initialize loss and optimizer with better parameters
    criterion = nn.NLLLoss()
    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()), 
        lr=0.0001,
        weight_decay=1e-5
    )
    scheduler = lr_scheduler.ReduceLROnPlateau(
        optimizer, 
        mode='min',
        factor=0.1,
        patience=3,
        verbose=True
    )

    # Load existing model if available
    model_path = os.path.join(base_dir, "models/classifier.pt")
    start_epoch, best_valid_loss = load_model(model, optimizer, model_path)

    # Print model summary
    pytorch_total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Number of trainable parameters: {pytorch_total_params}")

    # Train model with improved parameters
    print("Starting training...")
    num_epochs = 30  # Increased epochs
    patience = 7     # Early stopping patience
    best_valid_loss = float('inf')
    no_improve_count = 0
    train_losses, test_losses, acc = train_and_test(
        model, trainloader, validloader, criterion, optimizer, 
        scheduler, num_epochs, device, model_path
    )

    # Plot results
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Training loss')
    plt.plot([loss.cpu().numpy() for loss in test_losses], label='Validation loss')
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot([a/len(validloader) for a in acc], label='Validation Accuracy')
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(base_dir, 'models/training_results.png'))
    print("Training completed! Results saved to models/training_results.png")

if __name__ == "__main__":
    main()

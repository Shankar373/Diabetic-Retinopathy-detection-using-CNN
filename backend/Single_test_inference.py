#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import torch
from torch import nn
import torchvision
from torch.utils.data import Dataset, DataLoader
from PIL import Image, ImageFile
import os
import pandas as pd
ImageFile.LOAD_TRUNCATED_IMAGES = True
import cv2
import seaborn as sns

class CreateDataset(Dataset):
    def __init__(self, df_data, data_dir='../input/', transform=None):
        super().__init__()
        self.df = df_data.values
        self.data_dir = data_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        row = self.df[index]
        img_name, label = row[:2]
        img_path = os.path.join(self.data_dir, img_name)
        if not os.path.exists(img_path):
            print(f"Image file not found: {img_path}")
            return None, None
        
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform is not None:
                image = self.transform(image)
            return image, label, img_name  # Return filename for visualization
        except Exception as e:
            print(f"Failed to load image {img_path}: {str(e)}")
            return None, None, None

class CustomNet(nn.Module):
    def __init__(self):
        super(CustomNet, self).__init__()
        # Create ModuleList to store features
        self.features = nn.ModuleList([
            # Block 1 [0-4]
            nn.Conv2d(3, 16, kernel_size=3, padding=1),  # 0
            nn.BatchNorm2d(16),  # 1
            nn.ReLU(inplace=True),  # 2
            nn.MaxPool2d(kernel_size=2, stride=2),  # 3 - no params
            nn.Identity(),  # 4 - placeholder
            
            # Block 2 [5-9]
            nn.Conv2d(16, 32, kernel_size=3, padding=1),  # 5
            nn.BatchNorm2d(32),  # 6
            nn.ReLU(inplace=True),  # 7
            nn.MaxPool2d(kernel_size=2, stride=2),  # 8 - no params
            nn.Identity(),  # 9 - placeholder
            
            # Block 3 [10-14]
            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # 10
            nn.BatchNorm2d(64),  # 11
            nn.ReLU(inplace=True),  # 12
            nn.MaxPool2d(kernel_size=2, stride=2),  # 13 - no params
            nn.Identity(),  # 14 - placeholder
        ])
        
        self.avgpool = nn.AdaptiveAvgPool2d((4, 4))
        self.classifier = nn.Sequential(
            nn.Linear(1024, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(128, 5)
        )

    def forward(self, x):
        for layer in self.features:
            x = layer(x)
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

def load_model(path, device):
    print("Loading model from:", path)
    model = CustomNet()
    checkpoint = torch.load(path, map_location=device, weights_only=True)
    
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
    else:
        state_dict = checkpoint
    
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()
    return model

def visualize_predictions(images, true_labels, pred_labels, filenames, probabilities, save_path=None):
    classes = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']
    n = len(images)
    fig, axes = plt.subplots(2, n, figsize=(n*4, 8))
    
    # Plot images with predictions
    for i in range(n):
        # Convert tensor to image
        img = images[i].cpu().permute(1, 2, 0).numpy()
        # Denormalize
        img = img * np.array([0.229, 0.224, 0.225]) + np.array([0.485, 0.456, 0.406])
        img = np.clip(img, 0, 1)
        
        axes[0, i].imshow(img)
        axes[0, i].set_title(f'File: {filenames[i]}\nTrue: {classes[true_labels[i]]}\nPred: {classes[pred_labels[i]]}')
        axes[0, i].axis('off')
        
        # Plot probability distribution
        sns.barplot(x=classes, y=probabilities[i].cpu().numpy(), ax=axes[1, i])
        axes[1, i].set_xticklabels(classes, rotation=45)
        axes[1, i].set_title('Class Probabilities')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load and prepare data
test_csv = pd.read_csv('backend/models/testing.csv', usecols=['filename', 'label'])

# Define transforms
test_transforms = torchvision.transforms.Compose([
    torchvision.transforms.Resize((224, 224)),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
])

# Create dataset and dataloader
test_data = CreateDataset(df_data=test_csv, data_dir="backend/test/", transform=test_transforms)
test_loader = DataLoader(test_data, batch_size=4, shuffle=False)  # Smaller batch size for visualization

# Load model
model = load_model("backend/models/best_model.pth", device)

# Apply softmax to get probabilities
softmax = nn.Softmax(dim=1)

# Make predictions
with torch.no_grad():
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []
    all_images = []
    all_filenames = []

    for batch_idx, (inputs, labels, filenames) in enumerate(test_loader):
        if inputs is None or labels is None:
            continue
            
        inputs = inputs.to(device)
        labels = labels.to(device)
        
        outputs = model(inputs)
        probabilities = softmax(outputs)
        
        _, preds = torch.max(outputs, 1)
        
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        all_probs.append(probabilities)
        all_images.append(inputs)
        all_filenames.extend(filenames)
        
        # Visualize each batch
        visualize_predictions(
            inputs, 
            labels.cpu().numpy(), 
            preds.cpu().numpy(), 
            filenames,
            probabilities,
            save_path=f'backend/models/predictions_batch_{batch_idx}.png'
        )

# Print overall results
print("\nTest Results Summary:")
print("-" * 50)
classes = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']
for i, (pred, true, filename) in enumerate(zip(all_preds, all_labels, all_filenames)):
    print(f"Image: {filename}")
    print(f"True Class: {classes[true]}")
    print(f"Predicted Class: {classes[pred]}")
    print(f"Correct: {pred == true}")
    print("-" * 30)

# Calculate and print accuracy
accuracy = sum(p == t for p, t in zip(all_preds, all_labels)) / len(all_preds)
print(f"\nOverall Accuracy: {accuracy*100:.2f}%")

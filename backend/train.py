import torch
from torch import nn, optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from pathlib import Path
import logging
import argparse
from utils import DRDataGenerator
import numpy as np
import pandas as pd
from torchvision import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up CUDA if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f'Using device: {device}')

# Base directory setup
BASE_DIR = Path("/home/kasinadhsarma/dr-detection/backend")
TRAIN_DIR = BASE_DIR / "train"
MODEL_DIR = BASE_DIR / "models"

class EnhancedDRModel(nn.Module):
    def __init__(self, num_classes=5):
        super(EnhancedDRModel, self).__init__()
        self.backbone = models.resnet50(pretrained=True)
        
        # Freeze early layers
        for param in list(self.backbone.parameters())[:-30]:
            param.requires_grad = False
            
        num_ftrs = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(512, num_classes)
        )
        
    def forward(self, x):
        x = self.backbone(x)
        return F.log_softmax(x, dim=1)

def train(args):
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize metrics tracking
    metrics = {
        'epoch': [], 'train_loss': [], 'train_acc': [],
        'val_loss': [], 'val_acc': [], 'lr': []
    }
    
    train_dataset = DRDataGenerator(
        data_dir=TRAIN_DIR,
        training=True,
        target_size=(224, 224)
    )
    
    labels = [label for _, label in train_dataset]
    class_counts = np.bincount(labels)
    total_samples = len(labels)
    class_weights = torch.FloatTensor(total_samples / (len(class_counts) * class_counts)).to(device)
    
    generator = torch.Generator().manual_seed(42)
    train_size = int(0.8 * len(train_dataset))
    val_size = len(train_dataset) - train_size
    train_subset, val_subset = torch.utils.data.random_split(
        train_dataset, [train_size, val_size], generator=generator
    )
    
    train_loader = DataLoader(
        train_subset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_subset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )

    model = EnhancedDRModel(num_classes=5)
    if torch.cuda.device_count() > 1:
        model = nn.DataParallel(model)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    optimizer = optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=0.01,
        betas=(0.9, 0.999)
    )
    
    scheduler = optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=args.learning_rate,
        epochs=args.epochs,
        steps_per_epoch=len(train_loader),
        pct_start=0.3,
        anneal_strategy='cos'
    )

    scaler = torch.cuda.amp.GradScaler()
    best_val_accuracy = 0.0
    
    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (inputs, targets) in enumerate(train_loader):
            inputs, targets = inputs.to(device), targets.to(device)
            
            optimizer.zero_grad()
            
            with torch.cuda.amp.autocast():
                outputs = model(inputs)
                loss = criterion(outputs, targets)
            
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
            
            del outputs, loss
            torch.cuda.empty_cache()
            
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, targets in val_loader:
                inputs, targets = inputs.to(device), targets.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += targets.size(0)
                val_correct += predicted.eq(targets).sum().item()
                
                del outputs, loss
                torch.cuda.empty_cache()
        
        train_accuracy = 100. * correct / total
        val_accuracy = 100. * val_correct / val_total
        
        # Update metrics dictionary
        metrics['epoch'].append(epoch)
        metrics['train_loss'].append(train_loss/len(train_loader))
        metrics['train_acc'].append(train_accuracy)
        metrics['val_loss'].append(val_loss/len(val_loader))
        metrics['val_acc'].append(val_accuracy)
        metrics['lr'].append(optimizer.param_groups[0]['lr'])
        
        # Save metrics to CSV
        pd.DataFrame(metrics).to_csv(MODEL_DIR / 'training_metrics.csv', index=False)
        
        logger.info(
            f'Epoch {epoch + 1}/{args.epochs}: '
            f'Train Loss: {train_loss/len(train_loader):.4f}, '
            f'Train Acc: {train_accuracy:.2f}%, '
            f'Val Loss: {val_loss/len(val_loader):.4f}, '
            f'Val Acc: {val_accuracy:.2f}%, '
            f'LR: {optimizer.param_groups[0]["lr"]:.6f}'
        )

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            torch.save(model.state_dict(), MODEL_DIR / 'best_model.pth')
            logger.info(f"Saved best model with validation accuracy: {best_val_accuracy:.2f}%")

    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--learning-rate', type=float, default=3e-4)
    args = parser.parse_args()
    
    metrics = train(args)
    pd.DataFrame(metrics).to_csv(MODEL_DIR / 'final_training_metrics.csv', index=False)
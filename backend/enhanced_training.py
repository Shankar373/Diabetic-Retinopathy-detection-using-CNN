import torch
from torch import nn, optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from pathlib import Path
from tqdm import tqdm
import logging
import numpy as np
import matplotlib.pyplot as plt
import torchvision.transforms as transforms
from torchvision import models
from utils import DRDataGenerator
from IPython.display import clear_output

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up CUDA if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f'Using device: {device}')

# Define paths
BASE_DIR = Path("/home/kasinadhsarma/dr-detection/backend")
TRAIN_DIR = BASE_DIR / "train"
MODEL_DIR = BASE_DIR / "models"

# Create directories if they don't exist
MODEL_DIR.mkdir(parents=True, exist_ok=True)

class FocalLoss(nn.Module):
    def __init__(self, gamma=2, alpha=None):
        super(FocalLoss, self).__init__()
        self.gamma = gamma
        self.alpha = alpha
        
    def forward(self, input, target):
        ce_loss = F.cross_entropy(input, target, reduction='none', weight=self.alpha)
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma) * ce_loss
        return focal_loss.mean()

class EnhancedDRModel(nn.Module):
    def __init__(self, num_classes=5):
        super(EnhancedDRModel, self).__init__()
        
        # Use EfficientNetV2 Large backbone
        self.backbone = models.efficientnet_b7(pretrained=True)
        backbone_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Identity()
        
        # Multi-scale feature extraction
        self.conv1x1 = nn.Conv2d(backbone_features, 512, kernel_size=1)
        
        # Attention modules
        self.channel_attention = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(512, 128, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 512, kernel_size=1),
            nn.Sigmoid()
        )
        
        self.spatial_attention = nn.Sequential(
            nn.Conv2d(512, 1, kernel_size=7, padding=3),
            nn.Sigmoid()
        )
        
        # Advanced classifier with deep supervision
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(512, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(512, num_classes)
        )
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        # Extract backbone features
        x = self.backbone.extract_features(x)
        x = self.conv1x1(x)
        
        # Apply attention mechanisms
        ca = self.channel_attention(x)
        sa = self.spatial_attention(x)
        x = x * ca * sa
        
        # Classification
        out = self.classifier(x)
        return F.log_softmax(out, dim=1)

def train_model(batch_size=2, epochs=300, learning_rate=1e-4):  # Extended training with lower learning rate
    try:
        # Data augmentation for training
        train_transform = transforms.Compose([
            transforms.Resize((299, 299)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Validation transform
        val_transform = transforms.Compose([
            transforms.Resize((299, 299)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Initialize datasets
        train_dataset = DRDataGenerator(
            data_dir=TRAIN_DIR,
            training=True,
            target_size=(299, 299)  # Increased image size
        )

        # Calculate class weights for imbalanced dataset
        labels = []
        for idx in range(len(train_dataset)):
            try:
                _, label = train_dataset[idx]
                labels.append(label)
            except Exception as e:
                logger.warning(f"Error loading sample {idx}: {str(e)}")
                continue

        class_counts = np.bincount(labels)
        total_samples = len(labels)
        class_weights = torch.FloatTensor(total_samples / (len(class_counts) * class_counts)).to(device)

        # For small dataset, use simple random split while ensuring at least one sample per class
        from torch.utils.data import random_split
        
        # Calculate split sizes
        total_size = len(train_dataset)
        val_size = int(0.2 * total_size)
        train_size = total_size - val_size
        
        # Create splits
        train_subset, val_subset = random_split(
            train_dataset,
            [train_size, val_size],
            generator=torch.Generator().manual_seed(42)
        )

        # Create data loaders
        train_loader = DataLoader(
            train_subset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True
        )

        val_loader = DataLoader(
            val_subset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True
        )

        # Initialize model and training components
        model = EnhancedDRModel(num_classes=5).to(device)
        
        # Initialize Focal Loss with class weights
        criterion = FocalLoss(gamma=2, alpha=class_weights)
        
        # Use AdamW optimizer with weight decay
        optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
        
        # Learning rate scheduler with warmup
        from transformers import get_cosine_schedule_with_warmup
        num_training_steps = len(train_loader) * epochs
        num_warmup_steps = num_training_steps // 5  # Increased warmup steps
        scheduler = get_cosine_schedule_with_warmup(
            optimizer, 
            num_warmup_steps=num_warmup_steps,
            num_training_steps=num_training_steps
        )

        # Initialize automatic mixed precision scaler
        scaler = torch.cuda.amp.GradScaler()

        best_val_accuracy = 0.0
        early_stop_counter = 0
        history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}

        for epoch in range(epochs):
            # Training phase
            model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0

            for inputs, labels in tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}'):
                inputs, labels = inputs.to(device), labels.to(device)
                
                optimizer.zero_grad()
                
                # Use automatic mixed precision
                with torch.cuda.amp.autocast():
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)

                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()

                train_loss += loss.item()
                _, predicted = outputs.max(1)
                train_total += labels.size(0)
                train_correct += predicted.eq(labels).sum().item()

                scheduler.step()

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

            # Calculate metrics
            train_accuracy = train_correct / train_total
            val_accuracy = val_correct / val_total

            # Update history
            history['train_loss'].append(train_loss / len(train_loader))
            history['val_loss'].append(val_loss / len(val_loader))
            history['train_acc'].append(train_accuracy)
            history['val_acc'].append(val_accuracy)

            # Print progress
            logger.info(f'Epoch {epoch+1}/{epochs}:')
            logger.info(f'Train Loss: {train_loss/len(train_loader):.4f}, Train Acc: {train_accuracy:.4f}')
            logger.info(f'Val Loss: {val_loss/len(val_loader):.4f}, Val Acc: {val_accuracy:.4f}')

            # Save best model
            if val_accuracy > best_val_accuracy:
                best_val_accuracy = val_accuracy
                early_stop_counter = 0
                torch.save(model.state_dict(), MODEL_DIR / 'best_model.pth')
                logger.info(f'New best model saved with validation accuracy: {val_accuracy:.4f}')
            else:
                early_stop_counter += 1
                if early_stop_counter >= 30:  # Further increased patience for better convergence
                    logger.info('Early stopping triggered')
                    break

        # Plot training history
        plt.figure(figsize=(12, 4))
        plt.subplot(1, 2, 1)
        plt.plot(history['train_loss'], label='Train Loss')
        plt.plot(history['val_loss'], label='Val Loss')
        plt.title('Loss History')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(history['train_acc'], label='Train Acc')
        plt.plot(history['val_acc'], label='Val Acc')
        plt.title('Accuracy History')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()

        plt.tight_layout()
        plt.savefig(MODEL_DIR / 'training_results.png')
        plt.close()

        return history, best_val_accuracy

    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        raise

if __name__ == "__main__":
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    np.random.seed(42)
    
    history, best_accuracy = train_model()
    logger.info(f"Training completed. Best validation accuracy: {best_accuracy:.4f}")

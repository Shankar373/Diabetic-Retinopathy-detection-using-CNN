import torch
import torch.nn.functional as F
from pathlib import Path
import logging
from tqdm import tqdm
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from utils import DRDataGenerator
from enhanced_training import EnhancedDRModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Paths
BASE_DIR = Path("/home/kasinadhsarma/dr-detection/backend")
TEST_DIR = BASE_DIR / "test"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / 'best_model.pth'

def test_model():
    try:
        # Load model
        model = EnhancedDRModel(num_classes=5).to(device)
        model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()

        # Test data transform
        test_transform = transforms.Compose([
            transforms.Resize((299, 299)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Initialize test dataset
        test_dataset = DRDataGenerator(
            data_dir=TEST_DIR,
            training=False,
            target_size=(299, 299)  # Match training size
        )

        test_loader = DataLoader(
            test_dataset,
            batch_size=16,
            shuffle=False,
            num_workers=4,
            pin_memory=True
        )

        # Lists to store predictions and true labels
        all_predictions = []
        all_labels = []
        correct = 0
        total = 0

        # Test the model with TTA (Test Time Augmentation)
        with torch.no_grad():
            for images, labels in tqdm(test_loader, desc="Testing"):
                images, labels = images.to(device), labels.to(device)
                
                # Enhanced test-time augmentation
                outputs_list = []
                
                # Original image
                outputs_list.append(model(images))
                
                # Horizontal and vertical flips
                outputs_list.append(model(torch.flip(images, dims=[3])))  # horizontal
                outputs_list.append(model(torch.flip(images, dims=[2])))  # vertical
                
                # Multiple rotations
                angles = [-10, -5, 5, 10]
                for angle in angles:
                    rotated = transforms.functional.rotate(images, angle)
                    outputs_list.append(model(rotated))
                
                # Color jittering
                color_transform = transforms.ColorJitter(brightness=0.1, contrast=0.1)
                outputs_list.append(model(color_transform(images)))
                
                # Center crop with resize
                crop_transform = transforms.Compose([
                    transforms.CenterCrop(250),
                    transforms.Resize((299, 299))
                ])
                outputs_list.append(model(crop_transform(images)))
                
                # Average predictions with weights
                base_weight = 1.0
                flip_weight = 0.8
                rotation_weight = 0.6
                color_weight = 0.7
                crop_weight = 0.7
                
                weighted_sum = (
                    base_weight * outputs_list[0] +  # original
                    flip_weight * (outputs_list[1] + outputs_list[2]) +  # flips
                    rotation_weight * sum(outputs_list[3:7]) +  # rotations
                    color_weight * outputs_list[7] +  # color jittering
                    crop_weight * outputs_list[8]  # crop
                )
                
                total_weight = (base_weight + 2 * flip_weight + 
                              4 * rotation_weight + color_weight + crop_weight)
                outputs = weighted_sum / total_weight
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
                all_predictions.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

        # Calculate accuracy
        accuracy = 100 * correct / total
        logger.info(f'Test Accuracy: {accuracy:.2f}%')

        # Generate detailed metrics
        class_names = ['No DR', 'Mild DR', 'Moderate DR', 'Severe DR', 'Proliferative DR']
        
        # Classification report
        report = classification_report(all_labels, all_predictions, target_names=class_names)
        logger.info("\nClassification Report:\n" + report)

        # Confusion matrix
        cm = confusion_matrix(all_labels, all_predictions)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(MODEL_DIR / 'confusion_matrix.png')
        plt.close()

        # Save metrics to file
        with open(MODEL_DIR / 'test_results.txt', 'w') as f:
            f.write(f"Test Accuracy: {accuracy:.2f}%\n\n")
            f.write("Classification Report:\n")
            f.write(report)

        return accuracy

    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    np.random.seed(42)
    
    accuracy = test_model()
    logger.info(f"Testing completed. Final accuracy: {accuracy:.2f}%")

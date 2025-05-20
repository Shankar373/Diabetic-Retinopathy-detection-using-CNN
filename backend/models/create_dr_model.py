import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models

class DRModel(nn.Module):
    """
    Diabetic Retinopathy Detection Model based on ResNet18.
    """
    def __init__(self, num_classes=5):
        """
        Initialize the DRModel.

        Args:
            num_classes (int): Number of output classes.
        """
        super(DRModel, self).__init__()
        # Load a pre-trained ResNet18 model
        self.base_model = models.resnet18(pretrained=True)

        # Freeze early layers
        for param in self.base_model.parameters():
            param.requires_grad = False

        # Replace the final layer
        num_ftrs = self.base_model.fc.in_features
        self.base_model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        """
        Forward pass through the model.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor.
        """
        x = self.base_model(x)
        return x

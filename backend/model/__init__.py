"""Model package initialization."""
from pathlib import Path

# Set model directory
MODEL_DIR = Path(__file__).parent

# Import after directory setup
from .train import train

__all__ = ['train']

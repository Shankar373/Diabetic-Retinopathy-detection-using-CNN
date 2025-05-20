import os
import time
import torch
import torchvision.transforms as transforms
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
from PIL import Image
import io
import logging
from pathlib import Path
import pandas as pd
import socketio
from train import EnhancedDRModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
    handlers=[logging.FileHandler('dr_service.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class DRService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = Path('models/best_model.pth')
        self.severity_labels = ["No DR", "Mild DR", "Moderate DR", "Severe DR", "Proliferative DR"]
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.model = self.load_model()
        
    def load_model(self):
        try:
            model = EnhancedDRModel(num_classes=5).to(self.device)
            state_dict = torch.load(self.model_path, map_location=self.device)
            if 'model_state_dict' in state_dict:
                model.load_state_dict(state_dict['model_state_dict'])
            else:
                model.load_state_dict(state_dict)
            model.eval()
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return None

    async def preprocess_image(self, image_bytes):
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("Image too large")
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_tensor = self.transform(image)
        return img_tensor.unsqueeze(0).to(self.device)

    async def predict(self, image_tensor):
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]
            confidence, predicted = torch.max(probabilities, 0)
            return {
                'severity': self.severity_labels[predicted.item()],
                'confidence': confidence.item() * 100,
                'severity_scores': {
                    label: float(prob * 100)
                    for label, prob in zip(self.severity_labels, probabilities)
                }
            }

dr_service = DRService()

@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image_tensor = await dr_service.preprocess_image(contents)
        result = await dr_service.predict(image_tensor)
        return JSONResponse(content={"success": True, "data": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    try:
        df = pd.read_csv('models/training_metrics.csv')
        return {
            "success": True,
            "data": {
                "epochs": df['epoch'].tolist(),
                "train_acc": df['train_acc'].tolist(),
                "val_acc": df['val_acc'].tolist()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
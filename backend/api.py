import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import tensorflow as tf
import cv2
import numpy as np
from pipeline import main as train_model
from main import load_model

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.post("/train")
async def train(data_dir: str):
    try:
        logging.info("Starting model training...")
        train_model(Path(data_dir))
        logging.info("Model training completed.")
        return {"message": "Model training completed successfully."}
    except Exception as e:
        logging.error(f"An error occurred during training: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    try:
        logging.info("Loading the trained model...")
        model = load_model('best_model.h5')
        logging.info("Model loaded successfully.")

        logging.info("Predicting DR level for the uploaded image...")
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        prediction = model.predict(img)
        predicted_level = np.argmax(prediction, axis=1)[0]
        logging.info(f'Predicted DR level: {predicted_level}')
        return {"predicted_level": predicted_level}
    except Exception as e:
        logging.error(f"An error occurred during prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

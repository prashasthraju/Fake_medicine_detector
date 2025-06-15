from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
import numpy as np
from PIL import Image
import io
from resnet_extractor import extract_embeddings
from anomaly_detector import AnomalyDetector
import joblib
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Global variables for models
kmeans_detector = None
autoencoder_detector = None

def load_models():
    global kmeans_detector, autoencoder_detector
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load KMeans model
    kmeans_path = os.path.join(current_dir, 'kmeans_detector.joblib')
    if os.path.exists(kmeans_path):
        kmeans_detector = joblib.load(kmeans_path)
    
    # Load Autoencoder model
    autoencoder_path = os.path.join(current_dir, 'autoencoder_detector.pth')
    if os.path.exists(autoencoder_path):
        autoencoder_detector = AnomalyDetector(method='autoencoder')
        autoencoder_detector.autoencoder = autoencoder_detector.build_autoencoder()
        autoencoder_detector.autoencoder.load_state_dict(torch.load(autoencoder_path))
        autoencoder_detector.autoencoder.eval()

@app.on_event("startup")
async def startup_event():
    load_models()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save temporarily for feature extraction
        current_dir = os.path.dirname(os.path.abspath(__file__))
        temp_path = os.path.join(current_dir, "temp_image.jpg")
        image.save(temp_path)
        
        # Extract features
        features, _ = extract_embeddings(temp_path)
        
        # Remove temporary file
        os.remove(temp_path)
        
        # Get predictions from both models
        results = {}
        
        if kmeans_detector is not None:
            kmeans_pred = kmeans_detector.predict(features)
            results['kmeans'] = {
                'is_fake': bool(kmeans_pred[0]),
                'confidence': float(1 - kmeans_pred[0])  # Convert to confidence score
            }
        
        if autoencoder_detector is not None:
            autoencoder_pred = autoencoder_detector.predict(features)
            results['autoencoder'] = {
                'is_fake': bool(autoencoder_pred[0]),
                'confidence': float(1 - autoencoder_pred[0])  # Convert to confidence score
            }
        
        # Combine results
        if len(results) > 0:
            # If both models are available, use their average
            if 'kmeans' in results and 'autoencoder' in results:
                avg_confidence = (results['kmeans']['confidence'] + results['autoencoder']['confidence']) / 2
                is_fake = avg_confidence < 0.5
            else:
                # Use whichever model is available
                model_result = next(iter(results.values()))
                avg_confidence = model_result['confidence']
                is_fake = model_result['is_fake']
            
            return {
                "is_fake": is_fake,
                "confidence": avg_confidence,
                "model_details": results
            }
        else:
            raise HTTPException(status_code=500, detail="No models loaded")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "models_loaded": {
        "kmeans": kmeans_detector is not None,
        "autoencoder": autoencoder_detector is not None
    }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
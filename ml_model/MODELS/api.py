from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
import numpy as np
from PIL import Image
import io
from resnet_extractor import extract_embeddings, transform
from anomaly_detector import AnomalyDetector
import joblib
import os
import cv2
from typing import Dict, Any

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
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence threshold for predictions

def preprocess_image(image: Image.Image) -> Image.Image:
    """Enhanced image preprocessing"""
    # Convert to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY, 11, 2)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find the largest contour (assuming it's the medicine)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Add padding
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img_array.shape[1] - x, w + 2*padding)
        h = min(img_array.shape[0] - y, h + 2*padding)
        
        # Crop the image
        cropped = img_array[y:y+h, x:x+w]
        image = Image.fromarray(cropped)
    
    # Resize maintaining aspect ratio
    max_size = 800
    ratio = min(max_size/image.size[0], max_size/image.size[1])
    new_size = tuple(int(dim * ratio) for dim in image.size)
    image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    return image

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

def get_model_predictions(features: np.ndarray) -> Dict[str, Any]:
    """Get predictions from all available models with confidence scores"""
    results = {}
    
    if kmeans_detector is not None:
        kmeans_pred = kmeans_detector.predict(features)
        kmeans_proba = kmeans_detector.predict_proba(features)
        results['kmeans'] = {
            'is_fake': bool(kmeans_pred[0]),
            'confidence': float(kmeans_proba[0])
        }
    
    if autoencoder_detector is not None:
        autoencoder_pred = autoencoder_detector.predict(features)
        autoencoder_proba = autoencoder_detector.predict_proba(features)
        results['autoencoder'] = {
            'is_fake': bool(autoencoder_pred[0]),
            'confidence': float(autoencoder_proba[0])
        }
    
    return results

def ensemble_predictions(results: Dict[str, Any]) -> Dict[str, Any]:
    """Combine predictions from multiple models using weighted voting"""
    if not results:
        return {"is_fake": None, "confidence": 0.0, "model_details": results}
    
    # Calculate weighted average
    total_weight = 0
    weighted_sum = 0
    
    for model_name, result in results.items():
        # Weight based on confidence
        weight = result['confidence']
        total_weight += weight
        weighted_sum += weight * (0 if result['is_fake'] else 1)
    
    if total_weight == 0:
        return {"is_fake": None, "confidence": 0.0, "model_details": results}
    
    avg_confidence = weighted_sum / total_weight
    is_fake = avg_confidence < 0.5
    
    # Only return high-confidence predictions
    if avg_confidence < CONFIDENCE_THRESHOLD and avg_confidence > (1 - CONFIDENCE_THRESHOLD):
        return {
            "is_fake": is_fake,
            "confidence": avg_confidence,
            "model_details": results,
            "warning": "Low confidence prediction"
        }
    
    return {
        "is_fake": is_fake,
        "confidence": avg_confidence,
        "model_details": results
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhanced preprocessing
        image = preprocess_image(image)
        
        # Save temporarily for feature extraction
        current_dir = os.path.dirname(os.path.abspath(__file__))
        temp_path = os.path.join(current_dir, "temp_image.jpg")
        image.save(temp_path, quality=95)  # Save with high quality
        
        # Extract features
        features, _ = extract_embeddings(temp_path)
        
        # Remove temporary file
        os.remove(temp_path)
        
        # Get predictions from all models
        results = get_model_predictions(features)
        
        # Combine predictions using ensemble method
        if results:
            return ensemble_predictions(results)
        else:
            raise HTTPException(status_code=500, detail="No models loaded")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": {
            "kmeans": kmeans_detector is not None,
            "autoencoder": autoencoder_detector is not None
        },
        "confidence_threshold": CONFIDENCE_THRESHOLD
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
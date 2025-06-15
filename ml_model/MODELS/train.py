import torch
from anomaly_detector import AnomalyDetector
from resnet_extractor import extract_embeddings
import os

def train_models():
    print("Loading and extracting features from real medicine images...")
    test_images_path = os.path.join(os.path.dirname(__file__), "test_images")
    X, filenames = extract_embeddings(test_images_path)
    
    print("\nTraining KMeans Anomaly Detector...")
    kmeans_detector = AnomalyDetector(method='kmeans')
    kmeans_detector.fit(X)
    kmeans_detector.evaluate(X)
    
    print("\nTraining Autoencoder Anomaly Detector...")
    autoencoder_detector = AnomalyDetector(method='autoencoder')
    autoencoder_detector.fit(X)
    autoencoder_detector.evaluate(X)
    
    # Save the models
    print("\nSaving models...")
    import joblib
    joblib.dump(kmeans_detector, 'kmeans_detector.joblib')
    torch.save(autoencoder_detector.autoencoder.state_dict(), 'autoencoder_detector.pth')
    
    print("Models saved successfully!")

if __name__ == "__main__":
    train_models() 
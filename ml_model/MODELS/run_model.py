import os
import numpy as np
import shutil
from anomaly_detector import AnomalyDetector
from resnet_extractor import extract_embeddings
from sklearn.model_selection import train_test_split

def setup_test_data():
    """Set up test data by copying images from test_images to real_medicines and fake_medicines"""
    test_dir = "test_images"
    real_dir = "real_medicines"
    fake_dir = "fake_medicines"
    
    # Create directories if they don't exist
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)
    
    # Get all jpg images
    images = [f for f in os.listdir(test_dir) if f.endswith('.jpg')]
    
    # Split images into real and fake (for testing, we'll split them evenly)
    mid = len(images) // 2
    real_images = images[:mid]
    fake_images = images[mid:]
    
    # Copy images to respective directories
    for img in real_images:
        src = os.path.join(test_dir, img)
        dst = os.path.join(real_dir, img)
        shutil.copy2(src, dst)
    
    for img in fake_images:
        src = os.path.join(test_dir, img)
        dst = os.path.join(fake_dir, img)
        shutil.copy2(src, dst)
    
    print(f"Copied {len(real_images)} images to real_medicines")
    print(f"Copied {len(fake_images)} images to fake_medicines")

def main():
    print("Starting medicine authenticity detection model...")
    
    # Set up test data
    print("\nSetting up test data...")
    setup_test_data()
    
    print("\n1. Extracting features from images...")
    try:
        # Load features from real medicine images
        print("Processing real medicine images...")
        X_real, real_filenames = extract_embeddings("real_medicines")
        print(f"Processed {len(real_filenames)} real medicine images")
        
        # Load features from fake medicine images
        print("\nProcessing fake medicine images...")
        X_fake, fake_filenames = extract_embeddings("fake_medicines")
        print(f"Processed {len(fake_filenames)} fake medicine images")
        
        # Combine data for training
        X = np.vstack([X_real, X_fake])
        labels = np.array([0] * len(X_real) + [1] * len(X_fake))
        
        # Split into train and validation sets
        X_train, X_val, y_train, y_val = train_test_split(X, labels, test_size=0.2, random_state=42)
        
        print("\n2. Training KMeans Anomaly Detector...")
        kmeans_detector = AnomalyDetector(method='kmeans')
        kmeans_detector.fit(X_train, X_val, y_val)
        
        print("\n3. Training Autoencoder Anomaly Detector...")
        autoencoder_detector = AnomalyDetector(method='autoencoder')
        autoencoder_detector.fit(X_train, X_val, y_val)
        
        print("\n4. Evaluating models...")
        print("\nKMeans Model Evaluation:")
        kmeans_detector.evaluate(X_val, y_val)
        
        print("\nAutoencoder Model Evaluation:")
        autoencoder_detector.evaluate(X_val, y_val)
        
        print("\nModel training and evaluation completed successfully!")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
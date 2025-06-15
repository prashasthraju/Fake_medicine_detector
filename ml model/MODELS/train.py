import torch
import numpy as np
from anomaly_detector import AnomalyDetector
from resnet_extractor import extract_embeddings, fine_tune_model
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

def load_and_prepare_data():
    """Load and prepare the dataset"""
    print("Loading and preparing data...")
    
    # Load real medicine images
    real_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "real_medicines")
    if not os.path.exists(real_path):
        raise ValueError(f"Real medicines directory not found at {real_path}")
    
    # Load fake medicine images
    fake_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fake_medicines")
    if not os.path.exists(fake_path):
        raise ValueError(f"Fake medicines directory not found at {fake_path}")
    
    # Extract features
    print("Extracting features from real medicines...")
    X_real, real_filenames = extract_embeddings(real_path)
    print(f"Found {len(X_real)} real medicine images")
    
    print("Extracting features from fake medicines...")
    X_fake, fake_filenames = extract_embeddings(fake_path)
    print(f"Found {len(X_fake)} fake medicine images")
    
    # Combine data
    X = np.vstack([X_real, X_fake])
    y = np.array([0] * len(X_real) + [1] * len(X_fake))
    
    # Split into train and validation sets
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    return X_train, X_val, y_train, y_val

def plot_confusion_matrix(y_true, y_pred, title):
    """Plot confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(title)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(f'{title.lower().replace(" ", "_")}_confusion_matrix.png')
    plt.close()

def evaluate_model(model, X_val, y_val, model_name):
    """Evaluate model performance"""
    print(f"\nEvaluating {model_name}...")
    predictions = model.predict(X_val)
    probabilities = model.predict_proba(X_val)
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_val, predictions))
    
    # Plot confusion matrix
    plot_confusion_matrix(y_val, predictions, f"{model_name} Confusion Matrix")
    
    # Calculate and print accuracy
    accuracy = np.mean(predictions == y_val)
    print(f"\nAccuracy: {accuracy:.4f}")
    
    return accuracy

def train_models():
    """Train and evaluate both models"""
    try:
        # Load and prepare data
        X_train, X_val, y_train, y_val = load_and_prepare_data()
        
        # Fine-tune the feature extractor
        print("\nFine-tuning feature extractor...")
        fine_tune_model("real_medicines", "fake_medicines", epochs=20)
        
        # Train KMeans model
        print("\nTraining KMeans Anomaly Detector...")
        kmeans_detector = AnomalyDetector(method='kmeans', n_clusters=3)
        kmeans_detector.fit(X_train, X_val, y_val)
        kmeans_accuracy = evaluate_model(kmeans_detector, X_val, y_val, "KMeans")
        
        # Train Autoencoder model
        print("\nTraining Autoencoder Anomaly Detector...")
        autoencoder_detector = AnomalyDetector(method='autoencoder')
        autoencoder_detector.fit(X_train, X_val, y_val)
        autoencoder_accuracy = evaluate_model(autoencoder_detector, X_val, y_val, "Autoencoder")
        
        # Save the models
        print("\nSaving models...")
        joblib.dump(kmeans_detector, 'kmeans_detector.joblib')
        torch.save(autoencoder_detector.autoencoder.state_dict(), 'autoencoder_detector.pth')
        
        # Print final results
        print("\nTraining completed successfully!")
        print(f"KMeans Model Accuracy: {kmeans_accuracy:.4f}")
        print(f"Autoencoder Model Accuracy: {autoencoder_accuracy:.4f}")
        
    except Exception as e:
        print(f"Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    train_models() 
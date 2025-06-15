import torch
import torch.nn as nn
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, precision_recall_curve, average_precision_score
import matplotlib.pyplot as plt
from resnet_extractor import extract_embeddings

class AnomalyDetector:
    def __init__(self, method='autoencoder', n_clusters=3):
        self.method = method
        self.n_clusters = n_clusters
        self.kmeans = None
        self.autoencoder = None
        self.threshold = None
        self.best_threshold = None
        
    def build_autoencoder(self, input_dim=512):
        class AutoEncoder(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(input_dim, 256),
                    nn.BatchNorm1d(256),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(256, 128),
                    nn.BatchNorm1d(128),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(128, 64)
                )
                self.decoder = nn.Sequential(
                    nn.Linear(64, 128),
                    nn.BatchNorm1d(128),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(128, 256),
                    nn.BatchNorm1d(256),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(256, input_dim)
                )
                
            def forward(self, x):
                z = self.encoder(x)
                return self.decoder(z)
        
        return AutoEncoder()
    
    def find_optimal_threshold(self, scores, labels):
        precision, recall, thresholds = precision_recall_curve(labels, scores)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        best_idx = np.argmax(f1_scores)
        return thresholds[best_idx]
    
    def fit(self, X, validation_X=None, validation_labels=None):
        if self.method == 'kmeans':
            # Fit KMeans
            self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
            self.kmeans.fit(X)
            
            # Calculate distances to cluster centers
            distances = np.min(self.kmeans.transform(X), axis=1)
            
            if validation_X is not None and validation_labels is not None:
                val_distances = np.min(self.kmeans.transform(validation_X), axis=1)
                self.threshold = self.find_optimal_threshold(val_distances, validation_labels)
            else:
                # Set threshold as mean + 2*std of distances
                self.threshold = np.mean(distances) + 2 * np.std(distances)
            
        elif self.method == 'autoencoder':
            # Initialize and train autoencoder
            self.autoencoder = self.build_autoencoder(X.shape[1])
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.autoencoder = self.autoencoder.to(device)
            
            # Convert data to tensor
            X_tensor = torch.FloatTensor(X).to(device)
            
            # Training setup
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(self.autoencoder.parameters(), lr=1e-3, weight_decay=1e-5)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=5)
            
            # Training loop
            n_epochs = 100
            batch_size = 32
            n_batches = len(X) // batch_size
            best_loss = float('inf')
            patience = 10
            patience_counter = 0
            
            for epoch in range(n_epochs):
                epoch_loss = 0
                self.autoencoder.train()
                for i in range(n_batches):
                    start_idx = i * batch_size
                    end_idx = start_idx + batch_size
                    batch = X_tensor[start_idx:end_idx]
                    
                    optimizer.zero_grad()
                    output = self.autoencoder(batch)
                    loss = criterion(output, batch)
                    loss.backward()
                    optimizer.step()
                    
                    epoch_loss += loss.item()
                
                avg_loss = epoch_loss/n_batches
                scheduler.step(avg_loss)
                
                if avg_loss < best_loss:
                    best_loss = avg_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch+1}")
                    break
                
                if (epoch + 1) % 10 == 0:
                    print(f'Epoch [{epoch+1}/{n_epochs}], Loss: {avg_loss:.4f}')
            
            # Calculate reconstruction errors
            self.autoencoder.eval()
            with torch.no_grad():
                X_recon = self.autoencoder(X_tensor)
                recon_errors = torch.mean((X_tensor - X_recon) ** 2, dim=1).cpu().numpy()
            
            if validation_X is not None and validation_labels is not None:
                val_tensor = torch.FloatTensor(validation_X).to(device)
                with torch.no_grad():
                    val_recon = self.autoencoder(val_tensor)
                    val_errors = torch.mean((val_tensor - val_recon) ** 2, dim=1).cpu().numpy()
                self.threshold = self.find_optimal_threshold(val_errors, validation_labels)
            else:
                # Set threshold as mean + 2*std of reconstruction errors
                self.threshold = np.mean(recon_errors) + 2 * np.std(recon_errors)
    
    def predict(self, X):
        if self.method == 'kmeans':
            # Calculate distances to cluster centers
            distances = np.min(self.kmeans.transform(X), axis=1)
            return distances > self.threshold
            
        elif self.method == 'autoencoder':
            # Calculate reconstruction errors
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            X_tensor = torch.FloatTensor(X).to(device)
            self.autoencoder.eval()
            
            with torch.no_grad():
                X_recon = self.autoencoder(X_tensor)
                recon_errors = torch.mean((X_tensor - X_recon) ** 2, dim=1).cpu().numpy()
            
            return recon_errors > self.threshold
    
    def predict_proba(self, X):
        if self.method == 'kmeans':
            distances = np.min(self.kmeans.transform(X), axis=1)
            # Convert distances to probabilities (closer to 0 means more likely to be real)
            probs = 1 / (1 + np.exp(distances - self.threshold))
            return probs
            
        elif self.method == 'autoencoder':
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            X_tensor = torch.FloatTensor(X).to(device)
            self.autoencoder.eval()
            
            with torch.no_grad():
                X_recon = self.autoencoder(X_tensor)
                recon_errors = torch.mean((X_tensor - X_recon) ** 2, dim=1).cpu().numpy()
            
            # Convert reconstruction errors to probabilities
            probs = 1 / (1 + np.exp(recon_errors - self.threshold))
            return probs
    
    def evaluate(self, X, labels=None):
        if self.method == 'kmeans':
            # Calculate silhouette score
            labels = self.kmeans.labels_
            score = silhouette_score(X, labels)
            print(f"KMeans Silhouette Score: {score:.4f}")
            
            # Plot cluster distances
            distances = np.min(self.kmeans.transform(X), axis=1)
            plt.figure(figsize=(10, 5))
            plt.hist(distances, bins=50)
            plt.axvline(self.threshold, color='r', linestyle='--', label='Anomaly Threshold')
            plt.xlabel('Distance to Nearest Cluster Center')
            plt.ylabel('Count')
            plt.title('Distribution of Distances to Cluster Centers')
            plt.legend()
            plt.savefig('kmeans_distances.png')
            plt.close()
            
        elif self.method == 'autoencoder':
            # Calculate reconstruction errors
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            X_tensor = torch.FloatTensor(X).to(device)
            self.autoencoder.eval()
            
            with torch.no_grad():
                X_recon = self.autoencoder(X_tensor)
                recon_errors = torch.mean((X_tensor - X_recon) ** 2, dim=1).cpu().numpy()
            
            # Plot reconstruction errors
            plt.figure(figsize=(10, 5))
            plt.hist(recon_errors, bins=50)
            plt.axvline(self.threshold, color='r', linestyle='--', label='Anomaly Threshold')
            plt.xlabel('Reconstruction Error')
            plt.ylabel('Count')
            plt.title('Distribution of Reconstruction Errors')
            plt.legend()
            plt.savefig('autoencoder_errors.png')
            plt.close()
            
            if labels is not None:
                # Calculate and print evaluation metrics
                predictions = recon_errors > self.threshold
                accuracy = np.mean(predictions == labels)
                precision = np.mean(predictions[labels == 1])
                recall = np.mean(labels[predictions == 1])
                f1 = 2 * (precision * recall) / (precision + recall)
                
                print(f"\nEvaluation Metrics:")
                print(f"Accuracy: {accuracy:.4f}")
                print(f"Precision: {precision:.4f}")
                print(f"Recall: {recall:.4f}")
                print(f"F1 Score: {f1:.4f}")

def main():
    # Load features from real medicine images
    X_real, real_filenames = extract_embeddings("real_medicines")
    X_fake, fake_filenames = extract_embeddings("fake_medicines")
    
    # Combine data for training
    X = np.vstack([X_real, X_fake])
    labels = np.array([0] * len(X_real) + [1] * len(X_fake))
    
    # Split into train and validation sets
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X, labels, test_size=0.2, random_state=42)
    
    # Try both methods
    print("\nTraining KMeans Anomaly Detector...")
    kmeans_detector = AnomalyDetector(method='kmeans')
    kmeans_detector.fit(X_train, X_val, y_val)
    kmeans_detector.evaluate(X_val, y_val)
    
    print("\nTraining Autoencoder Anomaly Detector...")
    autoencoder_detector = AnomalyDetector(method='autoencoder')
    autoencoder_detector.fit(X_train, X_val, y_val)
    autoencoder_detector.evaluate(X_val, y_val)
    
    # Save the models
    if kmeans_detector.kmeans is not None:
        import joblib
        joblib.dump(kmeans_detector, 'kmeans_detector.joblib')
    
    if autoencoder_detector.autoencoder is not None:
        torch.save(autoencoder_detector.autoencoder.state_dict(), 'autoencoder_detector.pth')

if __name__ == "__main__":
    main() 
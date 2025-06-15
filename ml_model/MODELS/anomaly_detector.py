import torch
import torch.nn as nn
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from resnet_extractor import extract_embeddings

class AnomalyDetector:
    def __init__(self, method='autoencoder', n_clusters=3):
        self.method = method
        self.n_clusters = n_clusters
        self.kmeans = None
        self.autoencoder = None
        self.threshold = None
        
    def build_autoencoder(self, input_dim=512):
        class AutoEncoder(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(input_dim, 256),
                    nn.BatchNorm1d(256),
                    nn.ReLU(),
                    nn.Linear(256, 128),
                    nn.BatchNorm1d(128),
                    nn.ReLU(),
                    nn.Linear(128, 64)
                )
                self.decoder = nn.Sequential(
                    nn.Linear(64, 128),
                    nn.BatchNorm1d(128),
                    nn.ReLU(),
                    nn.Linear(128, 256),
                    nn.BatchNorm1d(256),
                    nn.ReLU(),
                    nn.Linear(256, input_dim)
                )
                
            def forward(self, x):
                z = self.encoder(x)
                return self.decoder(z)
        
        return AutoEncoder()
    
    def fit(self, X):
        if self.method == 'kmeans':
            # Fit KMeans
            self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
            self.kmeans.fit(X)
            
            # Calculate distances to cluster centers
            distances = np.min(self.kmeans.transform(X), axis=1)
            
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
            optimizer = torch.optim.Adam(self.autoencoder.parameters(), lr=1e-3)
            
            # Training loop
            n_epochs = 50
            batch_size = 32
            n_batches = len(X) // batch_size
            
            for epoch in range(n_epochs):
                epoch_loss = 0
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
                
                if (epoch + 1) % 10 == 0:
                    print(f'Epoch [{epoch+1}/{n_epochs}], Loss: {epoch_loss/n_batches:.4f}')
            
            # Calculate reconstruction errors
            self.autoencoder.eval()
            with torch.no_grad():
                X_recon = self.autoencoder(X_tensor)
                recon_errors = torch.mean((X_tensor - X_recon) ** 2, dim=1).cpu().numpy()
            
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
    
    def evaluate(self, X):
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

def main():
    # Load features from real medicine images
    X, filenames = extract_embeddings("real_medicines")
    
    # Try both methods
    print("\nTraining KMeans Anomaly Detector...")
    kmeans_detector = AnomalyDetector(method='kmeans')
    kmeans_detector.fit(X)
    kmeans_detector.evaluate(X)
    
    print("\nTraining Autoencoder Anomaly Detector...")
    autoencoder_detector = AnomalyDetector(method='autoencoder')
    autoencoder_detector.fit(X)
    autoencoder_detector.evaluate(X)
    
    # Save the models
    if kmeans_detector.kmeans is not None:
        import joblib
        joblib.dump(kmeans_detector, 'kmeans_detector.joblib')
    
    if autoencoder_detector.autoencoder is not None:
        torch.save(autoencoder_detector.autoencoder.state_dict(), 'autoencoder_detector.pth')

if __name__ == "__main__":
    main() 
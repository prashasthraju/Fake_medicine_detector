# resnet_extractor.py
import torch
from torchvision import models, transforms
from PIL import Image
import os
import numpy as np
from torch import nn
import torch.nn.functional as F

class FineTunedResNet(nn.Module):
    def __init__(self, pretrained=True):
        super().__init__()
        self.resnet = models.resnet50(pretrained=pretrained)
        # Remove the final fully connected layer
        self.resnet = nn.Sequential(*list(self.resnet.children())[:-1])
        
        # Add custom layers for medicine classification
        self.fc = nn.Sequential(
            nn.Linear(2048, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 512)  # Output embedding size
        )
        
    def forward(self, x):
        x = self.resnet(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return F.normalize(x, p=2, dim=1)  # L2 normalization

# Initialize the model
model = FineTunedResNet(pretrained=True)
model.eval()

# Image transformations
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                        [0.229, 0.224, 0.225])
])

def extract_embeddings(image_folder, batch_size=32):
    embeddings = []
    filenames = []
    
    # Get all image files
    image_files = [f for f in sorted(os.listdir(image_folder)) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Process images in batches
    for i in range(0, len(image_files), batch_size):
        batch_files = image_files[i:i + batch_size]
        batch_tensors = []
        
        for fname in batch_files:
            path = os.path.join(image_folder, fname)
            try:
                img = Image.open(path).convert("RGB")
                img_tensor = transform(img)
                batch_tensors.append(img_tensor)
                filenames.append(fname)
            except Exception as e:
                print(f"Error processing {fname}: {e}")
                continue
        
        if batch_tensors:
            # Stack tensors and get embeddings
            batch = torch.stack(batch_tensors)
            with torch.no_grad():
                batch_embeddings = model(batch).numpy()
            embeddings.extend(batch_embeddings)
    
    return np.array(embeddings), filenames

def fine_tune_model(train_folder, val_folder=None, epochs=10, learning_rate=1e-4):
    """
    Fine-tune the model on medicine images
    """
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.TripletMarginLoss(margin=1.0)
    
    # Load training data
    train_embeddings, _ = extract_embeddings(train_folder)
    
    # Training loop
    for epoch in range(epochs):
        epoch_loss = 0
        n_batches = len(train_embeddings) // batch_size
        
        for i in range(n_batches):
            start_idx = i * batch_size
            end_idx = start_idx + batch_size
            batch = train_embeddings[start_idx:end_idx]
            
            # Create triplets (anchor, positive, negative)
            # For simplicity, we'll use random triplets
            anchor_idx = np.random.randint(0, len(batch))
            positive_idx = np.random.randint(0, len(batch))
            while positive_idx == anchor_idx:
                positive_idx = np.random.randint(0, len(batch))
            
            negative_idx = np.random.randint(0, len(train_embeddings))
            while negative_idx == anchor_idx:
                negative_idx = np.random.randint(0, len(train_embeddings))
            
            anchor = torch.FloatTensor(batch[anchor_idx]).unsqueeze(0)
            positive = torch.FloatTensor(batch[positive_idx]).unsqueeze(0)
            negative = torch.FloatTensor(train_embeddings[negative_idx]).unsqueeze(0)
            
            optimizer.zero_grad()
            loss = criterion(anchor, positive, negative)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {epoch_loss/n_batches:.4f}")
    
    model.eval()
    return model

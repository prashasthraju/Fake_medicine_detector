# resnet_extractor.py
import torch
from torchvision import models, transforms
from PIL import Image
import os
import numpy as np

def get_device():
    """Get the appropriate device (CPU or GPU) for computation."""
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')

# Initialize ResNet with the new weights parameter
device = get_device()
resnet = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
resnet.fc = torch.nn.Identity()
resnet = resnet.to(device)
resnet.eval()

# Image transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                        [0.229, 0.224, 0.225])
])

def extract_embeddings(image_folder):
    """
    Extract embeddings from images in the specified folder.
    
    Args:
        image_folder (str): Path to the folder containing images
        
    Returns:
        tuple: (embeddings array, list of filenames)
    """
    if not os.path.exists(image_folder):
        raise ValueError(f"Image folder '{image_folder}' does not exist")
        
    embeddings = []
    filenames = []
    
    # Get all image files
    image_files = [f for f in sorted(os.listdir(image_folder)) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        raise ValueError(f"No image files found in '{image_folder}'")
    
    for fname in image_files:
        path = os.path.join(image_folder, fname)
        try:
            # Load and preprocess image
            img = Image.open(path).convert("RGB")
            img_tensor = transform(img).unsqueeze(0).to(device)
            
            # Extract features
            with torch.no_grad():
                emb = resnet(img_tensor).squeeze().cpu().numpy()
            
            embeddings.append(emb)
            filenames.append(fname)
            
        except Exception as e:
            print(f"Error processing {fname}: {str(e)}")
            continue
    
    if not embeddings:
        raise ValueError("No images were successfully processed")
    
    return np.array(embeddings), filenames

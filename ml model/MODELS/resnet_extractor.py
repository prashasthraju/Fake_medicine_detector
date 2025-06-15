# resnet_extractor.py
import torch
from torchvision import models, transforms
from PIL import Image
import os
import numpy as np

resnet = models.resnet18(pretrained=True)
resnet.fc = torch.nn.Identity()
resnet.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def extract_embeddings(image_folder):
    embeddings = []
    filenames = []
    for fname in sorted(os.listdir(image_folder)):
        if fname.endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(image_folder, fname)
            img = Image.open(path).convert("RGB")
            img_tensor = transform(img).unsqueeze(0)
            with torch.no_grad():
                emb = resnet(img_tensor).squeeze().numpy()
            embeddings.append(emb)
            filenames.append(fname)
    return np.array(embeddings), filenames

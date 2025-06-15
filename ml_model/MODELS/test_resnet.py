import os
from resnet_extractor import extract_embeddings

def test_extractor():
    # Create a test directory if it doesn't exist
    test_dir = "test_images"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"Created test directory: {test_dir}")
    
    try:
        # Try to extract embeddings
        embeddings, filenames = extract_embeddings(test_dir)
        print("Successfully imported and ran extract_embeddings")
        print(f"Number of embeddings: {len(embeddings)}")
        print(f"Number of filenames: {len(filenames)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_extractor() 
import numpy as np
import cv2
import matplotlib.pyplot as plt
from raster_to_vector import Vectorizer

def create_dummy_mask():
    """Creates a 512x512 mask with a simple wall layout."""
    mask = np.zeros((512, 512), dtype=np.uint8)
    
    # Outer walls
    mask[50:60, 50:450] = 1 # Top wall
    mask[450:460, 50:450] = 1 # Bottom wall
    mask[50:460, 50:60] = 1 # Left wall
    mask[50:460, 440:450] = 1 # Right wall
    
    # Inner wall
    mask[250:260, 50:250] = 1
    
    return mask

def test_classical_vectorizer():
    mask = create_dummy_mask()
    
    # Initialize the vectorizer with manhattan style (classical path)
    vectorizer = Vectorizer(style="manhattan")
    
    # Extract lines
    lines = vectorizer.process(mask)
    
    print(f"Extracted {len(lines)} lines from the mask.")
    
    # Visualize
    plt.figure(figsize=(10, 5))
    
    # Plot mask
    plt.subplot(1, 2, 1)
    plt.title("Input Wall Mask")
    plt.imshow(mask, cmap='gray')
    
    # Plot extracted lines
    plt.subplot(1, 2, 2)
    plt.title("Extracted Vector Lines")
    plt.imshow(mask, cmap='gray', alpha=0.3)
    
    for x1, y1, x2, y2 in lines:
        plt.plot([x1, x2], [y1, y2], color='red', linewidth=2)
        plt.scatter([x1, x2], [y1, y2], color='blue', s=10) # Plot endpoints
        
    plt.xlim(0, 512)
    plt.ylim(512, 0) # Invert y-axis to match image coordinates
    plt.tight_layout()
    plt.savefig('test_output.png')
    print("Saved visualization to test_output.png")

if __name__ == "__main__":
    test_classical_vectorizer()

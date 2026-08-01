import torch
print(f"CUDA: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'}")


get_ipython().getoutput("pip install -q segmentation-models-pytorch albumentations opencv-python torchmetrics cairosvg gdown")

import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")


get_ipython().getoutput("pip install -q segmentation-models-pytorch albumentations opencv-python torchmetrics")

from google.colab import drive
drive.mount('/content/drive')

import torch
print(f"CUDA: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'}")


get_ipython().getoutput("pip install -q gdown segmentation-models-pytorch albumentations opencv-python torchmetrics cairosvg")

# Download dataset directly
get_ipython().getoutput("gdown 1A5uPubXTHa-1DUSa7w3_5H1Se_t4zg8h -O /kaggle/working/dataset.zip")
get_ipython().getoutput("unzip -o -q /kaggle/working/dataset.zip -d /kaggle/working/dataset/")

# Verify
import os
base = '/kaggle/working/dataset/BIM_Vision/datasets/CubiCasa5K/cubicasa5k/high_quality_architectural'
print(f"Buildings: {len([f for f in os.listdir(base) if os.path.isdir(os.path.join(base, f))])}")


import os

# Check the path
base = '/kaggle/input/bim-dataset'
print("Contents:", os.listdir(base))

# Find where images are
for root, dirs, files in os.walk(base):
    if 'F1_original.png' in files:
        print(f"Found images at: {root}")
        break


import os
base = '/kaggle/input/bim-dataset'
print(os.path.exists(base))
if os.path.exists(base):
    print(os.listdir(base))


import os
print("Available inputs:", os.listdir('/kaggle/input/'))


import shutil
import os

# Clear everything in working directory
for item in os.listdir('/kaggle/working/'):
    path = os.path.join('/kaggle/working/', item)
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)

print("Working directory cleared!")
print("Free space:", os.listdir('/kaggle/working/'))


import os
print("Available inputs:", os.listdir('/kaggle/input/'))


import os

base = '/kaggle/input/datasets'
print("Contents:", os.listdir(base))

# Find where F1_original.png lives
for root, dirs, files in os.walk(base):
    if 'F1_original.png' in files:
        print(f"Found images at: {root}")
        print(f"Sample files: {files[:5]}")
        break


import os
import numpy as np
from PIL import Image
import cairosvg
import io
from scipy import ndimage
from tqdm import tqdm

CUBICASA_BASE = '/kaggle/input/datasets/marciarodrigo/bim-dataset/high_quality_architectural'
MASK_OUTPUT = '/kaggle/working/masks'
os.makedirs(MASK_OUTPUT, exist_ok=True)

def svg_to_mask(svg_path, target_size):
    w, h = target_size
    png_data = cairosvg.svg2png(url=svg_path, output_width=w, output_height=h)
    svg_img = Image.open(io.BytesIO(png_data)).convert('RGB')
    svg_array = np.array(svg_img)
    mask = np.zeros((h, w), dtype=np.uint8)
    
    room_mask = (svg_array[:,:,0] > 250) & (svg_array[:,:,1] > 250) & (svg_array[:,:,2] > 250)
    mask[room_mask] = 2
    
    window_mask = (svg_array[:,:,0] > 230) & (svg_array[:,:,0] < 250) & (svg_array[:,:,1] > 230) & (svg_array[:,:,2] > 250)
    mask[window_mask] = 4
    
    black_mask = (svg_array[:,:,0] < 50) & (svg_array[:,:,1] < 50) & (svg_array[:,:,2] < 50)
    room_dilated = ndimage.binary_dilation(room_mask, iterations=2)
    wall_mask = black_mask & room_dilated
    mask[wall_mask] = 1
    
    return mask

all_folders = sorted([f for f in os.listdir(CUBICASA_BASE) if os.path.isdir(os.path.join(CUBICASA_BASE, f))])

for folder in tqdm(all_folders):
    svg_path = os.path.join(CUBICASA_BASE, folder, 'model.svg')
    img_path = os.path.join(CUBICASA_BASE, folder, 'F1_original.png')
    mask_path = os.path.join(MASK_OUTPUT, f'{folder}.png')
    
    if os.path.exists(mask_path): 
        continue
    if not os.path.exists(svg_path) or not os.path.exists(img_path): 
        continue
    
    try:
        img = Image.open(img_path)
        mask = svg_to_mask(svg_path, img.size)
        Image.fromarray(mask).save(mask_path)
    except Exception as e:
        continue

print(f"Done! Masks: {len(os.listdir(MASK_OUTPUT))}")


import os
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader, random_split
import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torchmetrics import JaccardIndex
from tqdm import tqdm

DEVICE = torch.device("cuda")
BATCH_SIZE = 4
EPOCHS = 15
IMAGE_BASE = '/kaggle/input/datasets/marciarodrigo/bim-dataset/high_quality_architectural'
MASK_BASE = '/kaggle/working/masks'

class CubiCasaDataset(Dataset):
    def __init__(self, image_paths, mask_paths, transform=None):
        self.pairs = [(img, mask) for img, mask in zip(image_paths, mask_paths) 
                     if os.path.exists(img) and os.path.exists(mask)]
        self.transform = transform
        print(f"Valid pairs: {len(self.pairs)}")
    def __len__(self): 
        return len(self.pairs)
    def __getitem__(self, idx):
        img_path, mask_path = self.pairs[idx]
        image = np.array(Image.open(img_path).convert("RGB"))
        mask = np.array(Image.open(mask_path))
        if self.transform:
            augmented = self.transform(image=image, mask=mask)
            image, mask = augmented['image'], augmented['mask']
        return image, mask.long()

train_transform = A.Compose([
    A.Resize(512, 512), 
    A.HorizontalFlip(p=0.5), 
    A.RandomRotate90(p=0.5),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)), 
    ToTensorV2(),
])
val_transform = A.Compose([
    A.Resize(512, 512),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)), 
    ToTensorV2(),
])

building_ids = sorted([os.path.splitext(f)[0] for f in os.listdir(MASK_BASE) if f.endswith('.png')])
image_paths = [os.path.join(IMAGE_BASE, bid, 'F1_original.png') for bid in building_ids]
mask_paths = [os.path.join(MASK_BASE, f'{bid}.png') for bid in building_ids]

full = CubiCasaDataset(image_paths, mask_paths, transform=train_transform)
train_size = int(0.8 * len(full))
val_size = len(full) - train_size
train_ds, val_ds = random_split(full, [train_size, val_size])
val_ds.dataset.transform = val_transform

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=2, drop_last=True)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=2, drop_last=True)

model = smp.DeepLabV3Plus(encoder_name="resnet50", encoder_weights="imagenet", 
                          in_channels=3, classes=5, activation=None).to(DEVICE)

weights = torch.tensor([0.3, 2.0, 1.0, 1.5, 1.5]).to(DEVICE)
criterion = torch.nn.CrossEntropyLoss(weight=weights)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=3)

best_iou = 0.0
for epoch in range(EPOCHS):
    model.train()
    train_loss = 0.0
    for images, masks in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
        images, masks = images.to(DEVICE), masks.to(DEVICE)
        optimizer.zero_grad()
        loss = criterion(model(images), masks)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    
    model.eval()
    val_loss, val_iou_metric = 0.0, JaccardIndex(task="multiclass", num_classes=5, average=None).to(DEVICE)
    with torch.no_grad():
        for images, masks in val_loader:
            images, masks = images.to(DEVICE), masks.to(DEVICE)
            outputs = model(images)
            val_loss += criterion(outputs, masks).item()
            val_iou_metric.update(torch.argmax(outputs, dim=1), masks)
    
    scores = val_iou_metric.compute()
    mean_iou = scores[1:].mean().item()
    
    print(f"\nEpoch {epoch+1}: Train={train_loss/len(train_loader):.4f}, Val={val_loss/len(val_loader):.4f}")
    print(f"  IoU: BG={scores[0]:.3f}, Wall={scores[1]:.3f}, Room={scores[2]:.3f}, Door={scores[3]:.3f}, Win={scores[4]:.3f}")
    print(f"  Mean(no BG): {mean_iou:.4f}")
    
    if mean_iou > best_iou:
        best_iou = mean_iou
        torch.save(model.state_dict(), '/kaggle/working/best_model.pth')
        print(f"  ✓ Saved best model!")
    
    scheduler.step(mean_iou)

print(f"\n{'='*50}")
print(f"Training complete! Best Val IoU: {best_iou:.4f}")
print(f"{'='*50}")


import matplotlib.pyplot as plt
from IPython.display import FileLink

# Visualize predictions
model.eval()
images, masks = next(iter(val_loader))
images = images.to(DEVICE)

with torch.no_grad():
    preds = torch.argmax(model(images), dim=1)

images = images.cpu()
masks = masks.cpu()
preds = preds.cpu()

fig, axes = plt.subplots(3, 4, figsize=(16, 12))
for i in range(4):
    axes[0, i].imshow(images[i].permute(1, 2, 0) * 0.5 + 0.5)
    axes[0, i].set_title('Image')
    axes[0, i].axis('off')
    
    axes[1, i].imshow(masks[i], cmap='tab10', vmin=0, vmax=4)
    axes[1, i].set_title('Ground Truth')
    axes[1, i].axis('off')
    
    axes[2, i].imshow(preds[i], cmap='tab10', vmin=0, vmax=4)
    axes[2, i].set_title('Prediction')
    axes[2, i].axis('off')

plt.tight_layout()
plt.savefig('/kaggle/working/predictions.png')
plt.show()

# Download links
print("=" * 50)
print("DOWNLOAD YOUR FILES:")
print("=" * 50)
display(FileLink('/kaggle/working/best_model.pth'))
display(FileLink('/kaggle/working/predictions.png'))


import shutil
import os

# Zip your files
shutil.make_archive('/kaggle/working/BIM_Vision_Role5', 'zip', '/kaggle/working')

print("Zip created!")
print(os.path.getsize('/kaggle/working/BIM_Vision_Role5.zip') / 1e6, "MB")

import torch
import torch.nn as nn
import numpy as np

class DummyTransformerLearnedVectorizer(nn.Module):
    def __init__(self, input_channels=1, hidden_dim=256, num_queries=100):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(input_channels, 64, kernel_size=7, stride=2, padding=3),
            nn.ReLU(),
            nn.Conv2d(64, hidden_dim, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((16, 16))
        )
        
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=8, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        self.query_embed = nn.Embedding(num_queries, hidden_dim)
        
        self.bbox_head = nn.Linear(hidden_dim, 4) 
        self.prob_head = nn.Linear(hidden_dim, 1)

    def forward(self, mask: torch.Tensor):
        features = self.backbone(mask)
        B, C, H, W = features.shape
        features = features.view(B, C, -1).permute(0, 2, 1)
        
        encoded = self.transformer(features)
        
        queries = self.query_embed.weight.unsqueeze(0).repeat(B, 1, 1)
        attended_queries = queries + encoded.mean(dim=1, keepdim=True)
        
        bboxes = torch.sigmoid(self.bbox_head(attended_queries))
        probs = torch.sigmoid(self.prob_head(attended_queries))
        
        return bboxes, probs

class LearnedVectorizer:
    def __init__(self, model_path=None, device='cpu', prob_threshold=0.5):
        self.device = torch.device(device)
        self.model = DummyTransformerLearnedVectorizer().to(self.device)
        self.prob_threshold = prob_threshold
        
        if model_path:
            pass
            
        self.model.eval()

    def vectorize(self, mask: np.ndarray) -> list:
        if len(mask.shape) == 2:
            mask_tensor = torch.from_numpy(mask).float().unsqueeze(0).unsqueeze(0)
        elif len(mask.shape) == 3:
            mask_tensor = torch.from_numpy(mask).float().unsqueeze(0)
        else:
            raise ValueError(f"Unexpected mask shape: {mask.shape}")
            
        mask_tensor = mask_tensor.to(self.device)
        H_orig, W_orig = mask.shape[-2:]
        
        with torch.no_grad():
            bboxes, probs = self.model(mask_tensor)
            
        bboxes = bboxes.squeeze(0).cpu().numpy()
        probs = probs.squeeze(0).cpu().numpy()
        
        extracted_lines = []
        for i in range(len(probs)):
            if probs[i][0] > self.prob_threshold:
                x1, y1, x2, y2 = bboxes[i]
                line = [
                    int(x1 * W_orig),
                    int(y1 * H_orig),
                    int(x2 * W_orig),
                    int(y2 * H_orig)
                ]
                extracted_lines.append(line)
                
        return extracted_lines

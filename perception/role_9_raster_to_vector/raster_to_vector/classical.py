import cv2
import numpy as np
from skimage.morphology import skeletonize

class ClassicalVectorizer:
    def __init__(self, min_line_length=20, max_line_gap=10):
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap

    def vectorize(self, mask: np.ndarray) -> list:
        binary_mask = (mask > 0).astype(np.uint8)
        skeleton = skeletonize(binary_mask)
        skeleton_cv = (skeleton * 255).astype(np.uint8)
        
        lines = cv2.HoughLinesP(
            skeleton_cv, 
            rho=1, 
            theta=np.pi/180, 
            threshold=15, 
            minLineLength=self.min_line_length, 
            maxLineGap=self.max_line_gap
        )
        
        extracted_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line.flatten()
                extracted_lines.append([int(x1), int(y1), int(x2), int(y2)])
                
        regularized_lines = self._regularize_lines(extracted_lines)
        return regularized_lines
        
    def _regularize_lines(self, lines: list) -> list:
        regularized = []
        angle_tolerance = 10
        
        for x1, y1, x2, y2 in lines:
            dx = x2 - x1
            dy = y2 - y1
            angle = np.degrees(np.arctan2(dy, dx))
            
            if abs(angle) <= angle_tolerance or abs(abs(angle) - 180) <= angle_tolerance:
                y_avg = (y1 + y2) // 2
                regularized.append([x1, y_avg, x2, y_avg])
            elif abs(abs(angle) - 90) <= angle_tolerance:
                x_avg = (x1 + x2) // 2
                regularized.append([x_avg, y1, x_avg, y2])
            else:
                regularized.append([x1, y1, x2, y2])
                
        return regularized

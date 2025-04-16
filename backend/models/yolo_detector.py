import torch
import cv2
import numpy as np
from .base_detector import BaseDetector

class YOLODetector(BaseDetector):
    """Animal detector using YOLOv8"""
    
    def __init__(self, confidence_threshold=0.4):
        self.model = None
        self.confidence_threshold = confidence_threshold
        self._name = "yolov8"
        
        # COCO dataset animal classes
        self.animal_classes = [
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 
            'bear', 'zebra', 'giraffe', 'person'
        ]
    
    def load(self):
        """Load the YOLOv8 model"""
        try:
            # Use ultralytics package - YOLOv8 is more reliable
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")  # Load nano model (smallest and fastest)
        except ImportError:
            raise RuntimeError("ultralytics package not found. Install with: pip install ultralytics")
        
        return self
    
    def detect(self, frame):
        """Detect animals in a frame using YOLOv8"""
        if self.model is None:
            self.load()
        
        # Process frame with YOLOv8
        results = self.model(frame)
        
        # Filter for animals
        animal_detections = []
        animals_found = False
        
        # Process first result (single image)
        for r in results:
            # Extract boxes, confidences and class ids
            boxes = r.boxes
            
            for box in boxes:
                cls_id = int(box.cls[0].item())
                cls_name = r.names[cls_id]
                conf = float(box.conf[0].item())
                
                if cls_name in self.animal_classes and conf > self.confidence_threshold:
                    animals_found = True
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    animal_detections.append({
                        'class': cls_name,
                        'confidence': conf,
                        'bbox': [x1, y1, x2, y2]
                    })
        
        return {
            'has_animals': animals_found,
            'detections': animal_detections
        }
    
    @property
    def name(self):
        return self._name

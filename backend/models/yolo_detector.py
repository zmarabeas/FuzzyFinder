import torch
import cv2
from .base_detector import BaseDetector

class YOLODetector(BaseDetector):
    """Animal detector using YOLOv5"""
    
    def __init__(self, confidence_threshold=0.5, model_size='s'):
        self.model = None
        self.confidence_threshold = confidence_threshold
        self.model_size = model_size
        self._name = f"yolov5{model_size}"
        
        # COCO dataset animal classes that YOLO is trained on
        self.animal_classes = [
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 
            'bear', 'zebra', 'giraffe', 'person', 'mouse', 'rabbit'
        ]
    
    def load(self):
        """Load the YOLOv5 model"""
        # Load YOLOv5 from PyTorch Hub
        self.model = torch.hub.load('ultralytics/yolov5', f'yolov5{self.model_size}')
        return self
    
    def detect(self, frame):
        """Detect animals in a frame using YOLOv5"""
        if self.model is None:
            self.load()
        
        # Process a single frame with YOLOv5
        results = self.model(frame)
        
        # Filter for animals
        animal_detections = []
        animals_found = False
        
        # Parse results
        for *box, conf, cls_id in results.xyxy[0]:
            cls_name = results.names[int(cls_id)]
            if cls_name in self.animal_classes and conf > self.confidence_threshold:
                animals_found = True
                animal_detections.append({
                    'class': cls_name,
                    'confidence': float(conf),
                    'bbox': [float(box[0]), float(box[1]), float(box[2]), float(box[3])]
                })
        
        return {
            'has_animals': animals_found,
            'detections': animal_detections
        }
    
    @property
    def name(self):
        return self._name

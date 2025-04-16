import torch
import torchvision
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
import cv2
from .base_detector import BaseDetector

class MobileNetDetector(BaseDetector):
    """Animal detector using MobileNetV3 with SSDLite from torchvision"""
    
    def __init__(self, confidence_threshold=0.4):
        self.model = None
        self.confidence_threshold = confidence_threshold
        self._name = "mobilenet"
        
        # COCO dataset class mapping
        self.coco_classes = {
            1: 'person', 16: 'bird', 17: 'cat', 18: 'dog', 19: 'horse',
            20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
            24: 'zebra', 25: 'giraffe'
        }
        
        # Animal class IDs
        self.animal_classes = [16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    
    def load(self):
        """Load the MobileNetV3 model with SSDLite detection head"""
        # Load pre-trained model
        self.model = ssdlite320_mobilenet_v3_large(pretrained=True)
        self.model.eval()
        return self
    
    def detect(self, frame):
        """Detect animals in a frame using MobileNetV3"""
        if self.model is None:
            self.load()
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to tensor
        img_tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1).float() / 255.0
        
        # Run inference
        with torch.no_grad():
            prediction = self.model([img_tensor])
        
        # Extract predictions
        boxes = prediction[0]['boxes'].cpu()
        labels = prediction[0]['labels'].cpu()
        scores = prediction[0]['scores'].cpu()
        
        # Filter for animals with confidence above threshold
        animal_detections = []
        has_animals = False
        
        for box, label, score in zip(boxes, labels, scores):
            if label.item() in self.animal_classes and score.item() > self.confidence_threshold:
                has_animals = True
                animal_detections.append({
                    'class': self.coco_classes.get(label.item(), f"class_{label.item()}"),
                    'confidence': float(score.item()),
                    'bbox': box.tolist()
                })
        
        return {
            'has_animals': has_animals,
            'detections': animal_detections
        }
    
    @property
    def name(self):
        return self._name

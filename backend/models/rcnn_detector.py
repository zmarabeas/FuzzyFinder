from models.base_detector import BaseDetector
import torch
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2
import cv2

class FasterRCNNDetector(BaseDetector):
    """Animal detector using Faster R-CNN"""
    
    def __init__(self, confidence_threshold=0.5):
        self.model = None
        self.confidence_threshold = confidence_threshold
        self._name = "faster_rcnn"
        
        # COCO animal class IDs
        self.animal_class_ids = [
            1,  # person
            15, 16, 17, 18, 19, 20, 21, 22,  # animals
            23, 24, 25, 27,  # more animals
        ]
        
        # COCO class names
        self.class_names = {
            1: "person", 15: "bird", 16: "cat", 17: "dog", 18: "horse", 
            19: "sheep", 20: "cow", 21: "elephant", 22: "bear", 
            23: "zebra", 24: "giraffe", 25: "backpack", 27: "tie"
        }
    
    def load(self):
        """Load the Faster R-CNN model"""
        # Load a pre-trained Faster R-CNN model
        self.model = fasterrcnn_resnet50_fpn_v2(weights='DEFAULT')
        self.model.eval()
        return self
    
    def detect(self, frame):
        """Detect animals in a frame using Faster R-CNN"""
        if self.model is None:
            self.load()
        
        # Convert BGR to RGB (OpenCV uses BGR, PyTorch uses RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to tensor
        img_tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1).float() / 255.0
        
        # Run inference
        with torch.no_grad():
            prediction = self.model([img_tensor])
        
        # Extract predictions
        boxes = prediction[0]['boxes'].cpu().numpy()
        labels = prediction[0]['labels'].cpu().numpy()
        scores = prediction[0]['scores'].cpu().numpy()
        
        # Filter for animals with confidence above threshold
        animal_detections = []
        has_animals = False
        
        for box, label, score in zip(boxes, labels, scores):
            if label in self.animal_class_ids and score > self.confidence_threshold:
                has_animals = True
                animal_detections.append({
                    'class': self.class_names.get(label.item(), f"class_{label.item()}"),
                    'confidence': score.item(),
                    'bbox': box.tolist()
                })
        
        return {
            'has_animals': has_animals,
            'detections': animal_detections
        }
    
    @property
    def name(self):
        return self._name

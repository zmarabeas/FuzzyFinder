import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import cv2
import numpy as np
from .base_detector import BaseDetector

class ResNetDetector(BaseDetector):
    """Animal detector using ResNet50 pre-trained on ImageNet"""
    
    def __init__(self, confidence_threshold=0.5):
        self.model = None
        self.transform = None
        self.confidence_threshold = 0.3 #confidence_threshold
        self.imagenet_labels = None
        self._name = "resnet50"
        
        # Animal classes in ImageNet
        self.animal_classes = [
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 
            'bear', 'zebra', 'giraffe', 'monkey', 'fish', 'lion', 'tiger'
        ]
    
    def load(self):
        """Load the ResNet model and prepare transforms"""
        # Load pre-trained model
        self.model = models.resnet50(pretrained=True)
        self.model.eval()
        
        # Load ImageNet labels
        try:
            with open('imagenet_classes.txt') as f:
                self.imagenet_labels = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            # Default to numbered classes if file not found
            self.imagenet_labels = [f"class_{i}" for i in range(1000)]
        
        # Set up image transforms
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        return self
    
    def detect(self, frame):
        """Detect animals in a frame using ResNet50"""
        if self.model is None:
            self.load()
        
        # Convert from BGR to RGB (OpenCV uses BGR, PIL uses RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(frame_rgb)
        
        # Apply transformation
        img_tensor = self.transform(pil_image)
        img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
        
        # Get prediction
        with torch.no_grad():
            output = self.model(img_tensor)
            
        # Get top prediction
        _, predicted_idx = torch.max(output, 1)
        predicted_idx = predicted_idx.item()
        
        predicted_label = self.imagenet_labels[predicted_idx]
        is_animal = self._is_animal(predicted_label)
        
        # Create detection entry if it's an animal
        detections = []
        if is_animal:
            detections.append({
                'class': predicted_label,
                'confidence': float(torch.softmax(output, dim=1)[0, predicted_idx].item())
            })
        
        return {
            'has_animals': is_animal,
            'detections': detections
        }
    
    # def _is_animal(self, label):
    #     """Check if the label is an animal"""
    #     return any(animal in label.lower() for animal in self.animal_classes)
    def _is_animal(self, label):
        # Extensive list of ImageNet animal-related classes
        animal_classes = [
            # Dog breeds (dozens in ImageNet)
            'retriever', 'setter', 'terrier', 'hound', 'spaniel', 'bulldog', 'shepherd', 
            'collie', 'poodle', 'beagle', 'boxer', 'dalmatian', 'chihuahua', 'pug',
            # General animal categories
            'cat', 'bird', 'horse', 'sheep', 'cow', 'elephant', 'bear', 
            'zebra', 'giraffe', 'monkey', 'fish', 'lion', 'tiger',
            # More generic terms
            'animal', 'mammal', 'canine', 'feline', 'reptile', 'amphibian'
        ] + self.animal_classes
        
        # Print debug info
        # print(f"Checking label: {label}")
        is_match = any(animal in label.lower() for animal in animal_classes)
        # print(f"Is animal: {is_match}, confidence: {self.confidence_threshold}")
        
        return is_match
    
    @property
    def name(self):
        return self._name

import torch
import torch.nn as nn
import numpy as np
import cv2
from torchvision import transforms
from .base_detector import BaseDetector

class TemporalDetector(BaseDetector):
    """
    Temporal detector that wraps a base detector and adds LSTM-based
    temporal processing to improve detection consistency
    """
    
    def __init__(self, base_detector, sequence_length=5, hidden_size=128, num_layers=2):
        self.base_detector = base_detector
        self.sequence_length = sequence_length
        self.frame_buffer = []
        self.lstm_model = None
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self._name = f"temporal_{base_detector.name}"
        
    def load(self):
        """Load base detector and LSTM model"""
        # Ensure base detector is loaded
        if getattr(self.base_detector, 'model', None) is None:
            self.base_detector.load()
        
        # Initialize LSTM model
        feature_size = 80  # Default for YOLO models (80 COCO classes)
        if self.base_detector.name.startswith('resnet'):
            feature_size = 1000  # ImageNet classes for ResNet
        
        # Create LSTM model
        self.lstm_model = nn.Sequential(
            nn.LSTM(
                input_size=feature_size,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                batch_first=True
            ),
            nn.Linear(self.hidden_size, 1),
            nn.Sigmoid()
        )
        
        # Set to evaluation mode
        self.lstm_model[0].eval()
        
        return self
    
    def detect(self, frame):
        """
        Process frame with temporal context
        
        Note: First sequence_length-1 frames will return base detector results
        without temporal processing
        """
        # Get base detection result
        base_result = self.base_detector.detect(frame)
        
        # Add frame to buffer
        self.frame_buffer.append(frame)
        
        # Keep only the last sequence_length frames
        if len(self.frame_buffer) > self.sequence_length:
            self.frame_buffer.pop(0)
        
        # If we don't have enough frames yet, return base result
        if len(self.frame_buffer) < self.sequence_length:
            return base_result
        
        # Extract features from sequence
        features = self._extract_sequence_features()
        
        # Run through LSTM
        with torch.no_grad():
            temporal_score = self._process_sequence(features)
        
        # Update result with temporal info
        result = base_result.copy()
        result['temporal_confidence'] = temporal_score
        result['has_animals'] = temporal_score > 0.5  # Override with temporal decision
        
        return result
    
    def _extract_sequence_features(self):
        """Extract features from frame sequence using base detector"""
        # This implementation depends on the specific base detector
        # For simplicity, we'll use a placeholder
        features = []
        for frame in self.frame_buffer:
            result = self.base_detector.detect(frame)
            # Convert detection to a feature vector
            feature = np.zeros(80)  # Default for YOLO
            if self.base_detector.name.startswith('resnet'):
                feature = np.zeros(1000)  # ResNet
            
            for detection in result['detections']:
                if 'class_id' in detection:
                    feature[detection['class_id']] = detection['confidence']
            
            features.append(feature)
        
        return torch.tensor(features, dtype=torch.float32).unsqueeze(0)  # Add batch dim
    
    def _process_sequence(self, features):
        """Process sequence features with LSTM"""
        # Apply LSTM
        lstm_out, _ = self.lstm_model[0](features)
        
        # Get final output
        final_features = lstm_out[:, -1]
        output = self.lstm_model[1:](final_features)
        
        return float(output.item())
    
    @property
    def name(self):
        return self._name

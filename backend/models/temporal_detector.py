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
        self.detection_buffer = []  # Store detection results directly
        self.lstm = None
        self.fc = None
        self.sigmoid = None
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self._name = f"temporal_{base_detector.name}"
        self.class_mapping = {}  # To map class names to indices
        self.next_class_id = 0  # Counter for assigning class IDs
        
    def load(self):
        """Load base detector and LSTM model"""
        # Ensure base detector is loaded
        if getattr(self.base_detector, 'model', None) is None:
            self.base_detector.load()
        
        # Fixed feature size for all models to simplify
        feature_size = 128
        
        # Create LSTM components explicitly instead of Sequential
        self.lstm = nn.LSTM(
            input_size=feature_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            batch_first=True
        )
        
        self.fc = nn.Linear(self.hidden_size, 1)
        self.sigmoid = nn.Sigmoid()
        
        # Set to evaluation mode
        self.lstm.eval()
        self.fc.eval()
        
        return self
    
    def detect(self, frame):
        """
        Process frame with temporal context
        """
        # Get base detection result with lower threshold for better recall
        original_threshold = self.base_detector.confidence_threshold
        self.base_detector.confidence_threshold = 0.3  # Lower threshold for detection
        base_result = self.base_detector.detect(frame)
        self.base_detector.confidence_threshold = original_threshold  # Restore original
        
        # Add to buffers
        self.frame_buffer.append(frame)
        self.detection_buffer.append(base_result)
        
        # Keep only the last sequence_length frames
        if len(self.frame_buffer) > self.sequence_length:
            self.frame_buffer.pop(0)
            self.detection_buffer.pop(0)
        
        # If we don't have enough frames yet, return base result
        if len(self.frame_buffer) < self.sequence_length:
            return base_result
        
        # Check if any frame in sequence has animals
        # This is a simple fallback mechanism
        any_animals = any(result['has_animals'] for result in self.detection_buffer)
        
        if not any_animals:
            # No animals detected in any frame, skip LSTM
            result = base_result.copy()
            result['temporal_confidence'] = 0.0
            result['has_animals'] = False
            return result
            
        # Extract features from detection results
        features = self._extract_sequence_features()
        
        # Process with LSTM
        try:
            with torch.no_grad():
                # Process sequence
                lstm_out, _ = self.lstm(features)
                final_features = lstm_out[:, -1]
                logits = self.fc(final_features)
                temporal_score = float(self.sigmoid(logits).item())
                
                # Update result with temporal info
                result = base_result.copy()
                result['temporal_confidence'] = temporal_score
                
                # Lower threshold for temporal decision
                result['has_animals'] = temporal_score > 0.3
                
                return result
        except Exception as e:
            print(f"Error in LSTM processing: {e}")
            # Return base result as fallback
            return base_result
    
    def _extract_sequence_features(self):
        """Extract features from detection results"""
        # Fixed feature size
        feature_size = 128
        
        # Pre-allocate a numpy array for all features
        features_array = np.zeros((self.sequence_length, feature_size), dtype=np.float32)
        
        # Process each frame's detection results
        for i, result in enumerate(self.detection_buffer):
            # Feature 0: Has animals overall flag
            features_array[i, 0] = 1.0 if result['has_animals'] else 0.0
            
            # Feature 1: Number of detections
            features_array[i, 1] = min(len(result['detections']), 10) / 10.0
            
            # Process each detection
            for j, detection in enumerate(result['detections']):
                if j >= 10:  # Limit to 10 detections per frame
                    break
                    
                # Extract class name
                if 'class' in detection:
                    class_name = detection['class']
                    
                    # Map class name to index if not already mapped
                    if class_name not in self.class_mapping:
                        if self.next_class_id < feature_size - 20:  # Reserve space
                            self.class_mapping[class_name] = self.next_class_id + 20
                            self.next_class_id += 1
                        else:
                            # If we run out of space, use a hash
                            self.class_mapping[class_name] = hash(class_name) % (feature_size - 20) + 20
                    
                    # Set feature for this class
                    class_idx = self.class_mapping[class_name]
                    features_array[i, class_idx] = detection['confidence']
                
                # If we have bbox info, encode it as features
                if 'bbox' in detection:
                    bbox = detection['bbox']
                    if len(bbox) == 4:
                        # Normalize and store center coordinates and size
                        width = (bbox[2] - bbox[0]) / 1000.0  # Normalize
                        height = (bbox[3] - bbox[1]) / 1000.0
                        center_x = (bbox[0] + bbox[2]) / 2000.0
                        center_y = (bbox[1] + bbox[3]) / 2000.0
                        
                        # Store values in 4 features per detection (40 max)
                        base_idx = 2 + j * 4
                        if base_idx + 3 < 20:
                            features_array[i, base_idx] = center_x
                            features_array[i, base_idx + 1] = center_y
                            features_array[i, base_idx + 2] = width
                            features_array[i, base_idx + 3] = height
        
        # Convert directly to tensor
        return torch.from_numpy(features_array).unsqueeze(0)  # Add batch dim
    
    @property
    def name(self):
        return self._name
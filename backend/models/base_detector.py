from abc import ABC, abstractmethod

class BaseDetector(ABC):
    """Base class for all animal detectors"""
    
    @abstractmethod
    def load(self):
        """Load the model"""
        pass
        
    @abstractmethod
    def detect(self, frame):
        """
        Detect animals in a single frame
        
        Args:
            frame: CV2 image (BGR format)
            
        Returns:
            dict: Detection results with keys:
                - has_animals (bool): Whether animals were detected
                - detections (list): List of animal detections
        """
        pass
    
    @property
    @abstractmethod
    def name(self):
        """Return model name"""
        pass

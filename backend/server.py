from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
import cv2
import numpy as np

# Import our modules
from models.resnet_detector import ResNetDetector
from models.yolo_detector import YOLODetector
from models.temporal_detector import TemporalDetector
from utils.video_processor import extract_frames, find_animal_segments

app = Flask(__name__)
CORS(app)

''' Test route '''
@app.route('/', methods=['GET'])
def hello_world():
    response = jsonify({'message': 'Hello, World!'})
    return response

# Available detector factory
DETECTORS = {
    'resnet': lambda: ResNetDetector(confidence_threshold=0.5),
    'yolo': lambda: YOLODetector(confidence_threshold=0.5),
    'temporal_resnet': lambda: TemporalDetector(ResNetDetector(), sequence_length=5),
    'temporal_yolo': lambda: TemporalDetector(YOLODetector(), sequence_length=5)
}

@app.route('/process-video', methods=['POST'])
def process_video():
    """Process video and detect animals in frames"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    # Get detector type from request
    detector_type = request.form.get('detector', 'yolo')
    if detector_type not in DETECTORS:
        return jsonify({
            'error': f'Invalid detector type. Available options: {list(DETECTORS.keys())}'
        }), 400
    
    # Create detector
    detector = DETECTORS[detector_type]()
    detector.load()
    
    video_file = request.files['video']
    
    # Save uploaded video to a temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    video_file.save(temp_file.name)
    temp_file.close()
    
    try:
        # Extract frames
        video_data = extract_frames(temp_file.name)
        
        # Process each frame
        frame_results = []
        for i, frame in enumerate(video_data['frames']):
            result = detector.detect(frame)
            
            # Add frame metadata
            result['frame_number'] = i
            result['timestamp'] = i / video_data['fps']
            
            frame_results.append(result)
        
        # Find segments with animals
        segments = find_animal_segments(frame_results, video_data['fps'])
        
        # Prepare final result
        result = {
            'metadata': {
                'fps': video_data['fps'],
                'frame_count': video_data['frame_count'],
                'duration': video_data['duration'],
                'detector': detector.name
            },
            'frames': frame_results,
            'animal_segments': segments
        }
        
        return jsonify(result)
        
    finally:
        # Clean up temp file
        os.unlink(temp_file.name)

@app.route('/available-detectors', methods=['GET'])
def available_detectors():
    """Get list of available detectors"""
    return jsonify({
        'detectors': list(DETECTORS.keys()),
        'default': 'yolo'
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)

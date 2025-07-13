from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
import cv2
import numpy as np
from dataclasses import dataclass
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore

from celery.result import AsyncResult  # type: ignore

# Import our modules
from models.resnet_detector import ResNetDetector
from models.yolo_detector import YOLODetector
from models.temporal_detector import TemporalDetector
from models.rcnn_detector import FasterRCNNDetector
from models.ssd_detector import SSDDetector
from models.mobilenet_detector import MobileNetDetector
from utils.video_processor import extract_frames, find_animal_segments
from utils.youtube_downloader import download_youtube_video, InvalidYouTubeURLError, YouTubeDownloadError
from backend.task_queue import get_status
from backend.tasks import process_youtube as celery_process_youtube

app = Flask(__name__)
CORS(app)
# Rate limiter (100 requests per hour per IP)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["100 per hour"])

''' Test route '''
@app.route('/', methods=['GET'])
def hello_world():
    response = jsonify({'message': 'Hello, World!'})
    return response

# Available detector factory
DETECTORS = {
    'resnet': lambda: ResNetDetector(confidence_threshold=0.3),
    'yolo': lambda: YOLODetector(confidence_threshold=0.3),
    'faster_rcnn': lambda: FasterRCNNDetector(confidence_threshold=0.4),
    'ssd': lambda: SSDDetector(confidence_threshold=0.4),
    'mobilenet': lambda: MobileNetDetector(confidence_threshold=0.4),
    'temporal_mobilenet': lambda: TemporalDetector(MobileNetDetector(confidence_threshold=0.4), sequence_length=5),
    'temporal_resnet': lambda: TemporalDetector(ResNetDetector(confidence_threshold=0.3), sequence_length=5),
    'temporal_yolo': lambda: TemporalDetector(YOLODetector(confidence_threshold=0.4), sequence_length=5),
    'temporal_faster_rcnn': lambda: TemporalDetector(FasterRCNNDetector(confidence_threshold=0.4), sequence_length=5),
    'temporal_ssd': lambda: TemporalDetector(SSDDetector(confidence_threshold=0.4), sequence_length=5),
}


@dataclass
class YouTubeRequest:
    """Payload schema for /process-youtube route."""
    url: str
    detector: str = 'yolo'

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
            print(f'processing frame {i}/{video_data["frame_count"]}')
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

# Added stub endpoint for YouTube processing

@app.route('/process-youtube', methods=['POST'])
def process_youtube():
    """Placeholder route to process YouTube videos for animal detection.
    Expects JSON body with a 'url' field containing the YouTube video URL.
    Currently returns HTTP 501 (Not Implemented)."""
    data = request.get_json(force=True, silent=True) or {}
    req = YouTubeRequest(url=data.get('url', ''), detector=data.get('detector', 'yolo'))

    if not req.url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    # TODO: download YouTube video, extract frames, and run detection using req.detector
    try:
        celery_async_result = celery_process_youtube.apply_async(args=[req.url, req.detector])
        return jsonify({'task_id': celery_async_result.id, 'status': 'queued'}), 202
    except InvalidYouTubeURLError as e:
        return jsonify({'error': str(e)}), 400
    except YouTubeDownloadError as e:
        return jsonify({'error': str(e)}), 502


@app.route('/job-status/<int:job_id>', methods=['GET'])
def job_status(job_id: int):
    """Return status string for given job id"""
    return jsonify({'job_id': job_id, 'status': get_status(job_id)})

@app.route('/task-status/<task_id>', methods=['GET'])
@limiter.exempt
def task_status(task_id: str):
    """Return Celery task status."""
    res = AsyncResult(task_id)
    return jsonify({'task_id': task_id, 'state': res.state, 'successful': res.successful()})

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
    # app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(port=5005)

import cv2
import os
import numpy as np
import tempfile

def extract_frames(video_path, skip_frames=0):
    """
    Extract frames from video
    
    Args:
        video_path: Path to video file
        skip_frames: Process every Nth frame (0 = process all)
        
    Returns:
        dict: Video info with keys:
            - frames: List of frames
            - fps: Frames per second
            - frame_count: Total frame count
            - duration: Video duration in seconds
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    frames = []
    frame_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Skip frames if requested
        if skip_frames > 0 and frame_idx % (skip_frames + 1) != 0:
            frame_idx += 1
            continue
            
        frames.append(frame)
        frame_idx += 1
    
    cap.release()
    
    return {
        'frames': frames,
        'fps': fps,
        'frame_count': frame_count,
        'duration': duration
    }

def find_animal_segments(frame_results, fps):
    """
    Find segments of video that contain animals
    
    Args:
        frame_results: List of detection results per frame
        fps: Frames per second of the video
        
    Returns:
        list: List of segments with keys:
            - start_frame: Starting frame index
            - end_frame: Ending frame index
            - start_time: Starting time in seconds
            - end_time: Ending time in seconds
            - duration: Duration in seconds
    """
    segments = []
    in_segment = False
    start_frame = 0
    
    for i, result in enumerate(frame_results):
        has_animal = result.get('has_animals', False)
        
        if has_animal and not in_segment:
            # Start of a new segment
            in_segment = True
            start_frame = i
        elif not has_animal and in_segment:
            # End of a segment
            in_segment = False
            segments.append({
                'start_frame': start_frame,
                'end_frame': i - 1,
                'start_time': start_frame / fps,
                'end_time': (i - 1) / fps,
                'duration': (i - 1 - start_frame) / fps
            })
    
    # Check if we ended while still in a segment
    if in_segment:
        segments.append({
            'start_frame': start_frame,
            'end_frame': len(frame_results) - 1,
            'start_time': start_frame / fps,
            'end_time': (len(frame_results) - 1) / fps,
            'duration': (len(frame_results) - 1 - start_frame) / fps
        })
    
    return segments

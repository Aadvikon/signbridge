"""
MediaPipe Landmark Extraction Service
Extracts hand and pose landmarks from sign language videos using MediaPipe.
Processes videos frame-by-frame and saves landmark data for ML training.
"""

import cv2
import mediapipe as mp
import numpy as np
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LandmarkExtractor:
    """
    MediaPipe-based landmark extraction for sign language videos.
    Extracts hand and pose keypoints from video frames.
    """

    def __init__(self, confidence_threshold: float = 0.5, model_dir: str = None):
        """
        Initialize MediaPipe solutions.

        Args:
            confidence_threshold: Minimum confidence for landmark detection
            model_dir: Directory containing model files (default: models/)
        """
        self.confidence_threshold = confidence_threshold

        if model_dir is None:
            model_dir = Path(__file__).parent.parent.parent / "models"

        # Initialize MediaPipe tasks
        base_options = mp.tasks.BaseOptions

        # Model file paths
        hand_model_path = Path(model_dir) / "hand_landmarker.task"
        pose_model_path = Path(model_dir) / "pose_landmarker.task"

        if not hand_model_path.exists():
            raise FileNotFoundError(f"Hand model not found: {hand_model_path}")
        if not pose_model_path.exists():
            raise FileNotFoundError(f"Pose model not found: {pose_model_path}")

        # Initialize hand landmarker
        self.hand_landmarker = mp.tasks.vision.HandLandmarker.create_from_options(
            mp.tasks.vision.HandLandmarkerOptions(
                base_options=base_options(model_asset_path=str(hand_model_path)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,
                num_hands=2,
                min_hand_detection_confidence=self.confidence_threshold,
                min_hand_presence_confidence=self.confidence_threshold,
                min_tracking_confidence=self.confidence_threshold
            )
        )

        # Initialize pose landmarker
        self.pose_landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(
            mp.tasks.vision.PoseLandmarkerOptions(
                base_options=base_options(model_asset_path=str(pose_model_path)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,
                min_pose_detection_confidence=self.confidence_threshold,
                min_pose_presence_confidence=self.confidence_threshold,
                min_tracking_confidence=self.confidence_threshold
            )
        )

        logger.info(f"Initialized MediaPipe detectors (confidence: {self.confidence_threshold})")
        logger.info(f"Hand model: {hand_model_path}")
        logger.info(f"Pose model: {pose_model_path}")

    def extract_frame_landmarks(self, frame: np.ndarray, timestamp_ms: int) -> Dict:
        """
        Extract landmarks from a single frame.

        Args:
            frame: RGB frame from video
            timestamp_ms: Timestamp in milliseconds for video processing

        Returns:
            Dictionary containing landmark data for the frame
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Process with MediaPipe
        hand_result = self.hand_landmarker.detect_for_video(mp_image, timestamp_ms)
        pose_result = self.pose_landmarker.detect_for_video(mp_image, timestamp_ms)

        # Extract hand landmarks
        left_hand = self._extract_hand_landmarks(hand_result, "left")
        right_hand = self._extract_hand_landmarks(hand_result, "right")

        # Extract pose landmarks (focus on upper body)
        pose_landmarks = self._extract_pose_landmarks(pose_result)

        # Determine hand presence
        hand_presence = 0
        if left_hand is not None:
            hand_presence += 1
        if right_hand is not None:
            hand_presence += 2

        return {
            "hand_presence": hand_presence,  # 0=none, 1=left, 2=right, 3=both
            "left_hand": left_hand,
            "right_hand": right_hand,
            "pose": pose_landmarks
        }

    def _extract_hand_landmarks(self, result, hand_type: str) -> Optional[List[List[float]]]:
        """
        Extract hand landmarks for left or right hand.

        Args:
            result: MediaPipe HandLandmarkerResult
            hand_type: "left" or "right"

        Returns:
            List of [x, y, z, confidence] for 21 landmarks, or None if not detected
        """
        if not result.hand_landmarks:
            return None

        # Find the correct hand based on index (assuming first is right, second is left)
        # Note: This is a simplification; in practice, you might need better handedness detection
        hand_idx = 0 if hand_type == "right" else 1

        if hand_idx >= len(result.hand_landmarks):
            return None

        hand_landmarks = result.hand_landmarks[hand_idx]

        # Extract 21 landmarks (x, y, z)
        landmarks = []
        for landmark in hand_landmarks:
            landmarks.append([
                landmark.x,
                landmark.y,
                landmark.z,
                1.0  # No confidence in new API, use 1.0
            ])
        return landmarks

    def _extract_pose_landmarks(self, result) -> Optional[List[List[float]]]:
        """
        Extract pose landmarks (upper body focus).

        Args:
            result: MediaPipe PoseLandmarkerResult

        Returns:
            List of [x, y, z, confidence] for upper body landmarks
        """
        if not result.pose_landmarks:
            return None

        pose_landmarks = result.pose_landmarks[0]  # Get first pose

        # Upper body landmark indices (shoulders, elbows, wrists, face)
        upper_body_indices = [
            0,  # nose
            11, 12,  # shoulders
            13, 14,  # elbows
            15, 16,  # wrists
            17, 18,  # pinkies
            19, 20,  # indexes
            21, 22   # thumbs
        ]

        landmarks = []
        for idx in upper_body_indices:
            landmark = pose_landmarks[idx]
            landmarks.append([
                landmark.x,
                landmark.y,
                landmark.z,
                1.0  # No confidence in new API, use 1.0
            ])

        return landmarks

    def draw_landmarks_on_frame(self, frame: np.ndarray, landmarks: Dict) -> np.ndarray:
        """
        Draw landmarks on a frame for visualization.

        Args:
            frame: Original frame
            landmarks: Landmark data from extract_frame_landmarks

        Returns:
            Frame with landmarks drawn
        """
        # For now, just return the original frame since the drawing API has changed
        # TODO: Implement drawing with new MediaPipe task API
        return frame

    def _create_dummy_hand_results(self, landmarks: Dict):
        """Create dummy hand results for drawing."""
        class DummyResults:
            def __init__(self):
                self.multi_hand_landmarks = []
                self.multi_handedness = []

        results = DummyResults()

        # Add left hand if present
        if landmarks.get("left_hand"):
            hand_landmarks = self._list_to_mediapipe_landmarks(landmarks["left_hand"])
            results.multi_hand_landmarks.append(hand_landmarks)
            results.multi_handedness.append(type('obj', (object,), {'classification': [type('obj', (object,), {'label': 'Left'})()]}))

        # Add right hand if present
        if landmarks.get("right_hand"):
            hand_landmarks = self._list_to_mediapipe_landmarks(landmarks["right_hand"])
            results.multi_hand_landmarks.append(hand_landmarks)
            results.multi_handedness.append(type('obj', (object,), {'classification': [type('obj', (object,), {'label': 'Right'})()]}))

        return results

    def _create_dummy_pose_results(self, landmarks: Dict):
        """Create dummy pose results for drawing."""
        class DummyResults:
            def __init__(self):
                self.pose_landmarks = None

        results = DummyResults()

        if landmarks.get("pose"):
            results.pose_landmarks = self._list_to_mediapipe_landmarks(landmarks["pose"])

        return results

    def _list_to_mediapipe_landmarks(self, landmark_list: List[List[float]]):
        """Convert list of landmarks to MediaPipe format."""
        landmarks = []
        for lm in landmark_list:
            landmark = type('obj', (object,), {
                'x': lm[0],
                'y': lm[1],
                'z': lm[2],
                'visibility': lm[3] if len(lm) > 3 else 1.0
            })()
            landmarks.append(landmark)

        # Create landmark list object
        landmark_list_obj = type('obj', (object,), {'landmark': landmarks})()
        return landmark_list_obj

    def process_video(self, video_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Process entire video and extract landmarks from all frames.

        Args:
            video_path: Path to input video
            output_path: Optional path to save annotated video

        Returns:
            Dictionary with processing results and frame landmarks
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        logger.info(f"Processing video: {video_path}")

        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logger.info(f"Video info: {width}x{height}, {fps} FPS, {total_frames} frames")

        # Prepare output video if requested
        out_writer = None
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            logger.info(f"Saving annotated video to: {output_path}")

        # Process frames
        frame_landmarks = []
        processed_frames = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Extract landmarks
            timestamp_ms = int((processed_frames / fps) * 1000)  # Convert frame number to milliseconds
            landmarks = self.extract_frame_landmarks(frame, timestamp_ms)
            frame_landmarks.append({
                "frame_id": processed_frames,
                "timestamp_ms": timestamp_ms,
                "landmarks": landmarks
            })

            # Draw landmarks if saving output video
            if out_writer:
                annotated_frame = self.draw_landmarks_on_frame(frame, landmarks)
                out_writer.write(annotated_frame)

            processed_frames += 1

            # Progress logging
            if processed_frames % 50 == 0:
                logger.info(f"Processed {processed_frames}/{total_frames} frames")

        # Cleanup
        cap.release()
        if out_writer:
            out_writer.release()

        logger.info(f"✅ Processed {processed_frames} frames")
        logger.info(f"   Hand landmarks detected in {sum(1 for f in frame_landmarks if f['landmarks']['hand_presence'] > 0)} frames")

        return {
            "video_path": str(video_path),
            "total_frames": processed_frames,
            "fps": fps,
            "resolution": f"{width}x{height}",
            "frame_landmarks": frame_landmarks,
            "output_video": str(output_path) if output_path else None
        }

    def save_landmarks_json(self, results: Dict, output_path: str) -> None:
        """
        Save landmark extraction results to JSON file.

        Args:
            results: Results from process_video
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare JSON data
        json_data = {
            "video_info": {
                "path": results["video_path"],
                "total_frames": results["total_frames"],
                "fps": results["fps"],
                "resolution": results["resolution"]
            },
            "extraction_config": {
                "confidence_threshold": self.confidence_threshold,
                "mediapipe_version": mp.__version__
            },
            "frame_landmarks": results["frame_landmarks"]
        }

        with open(output_path, 'w') as f:
            json.dump(json_data, f, indent=2)

        logger.info(f"Saved landmarks to: {output_path}")

    def close(self):
        """Clean up MediaPipe resources."""
        self.hand_landmarker.close()
        self.pose_landmarker.close()
        logger.info("MediaPipe resources cleaned up")

    def process_all_videos(self, raw_data_path: str, landmarks_path: str) -> Dict:
        """
        Process all videos in the raw data directory and save landmarks as JSON.

        Args:
            raw_data_path: Path to data/raw/ directory
            landmarks_path: Path to data/landmarks/ directory

        Returns:
            Dictionary with processing statistics
        """
        raw_data_path = Path(raw_data_path)
        landmarks_path = Path(landmarks_path)

        if not raw_data_path.exists():
            raise FileNotFoundError(f"Raw data path not found: {raw_data_path}")

        landmarks_path.mkdir(parents=True, exist_ok=True)

        # Find all video files
        video_files = list(raw_data_path.rglob("*.mp4"))
        if not video_files:
            logger.warning(f"No video files found in {raw_data_path}")
            return {"total_videos": 0, "processed_videos": 0, "errors": 0}

        logger.info(f"Found {len(video_files)} video files to process")

        processed_count = 0
        error_count = 0
        total_frames = 0

        for video_file in video_files:
            try:
                # Create output path maintaining directory structure
                relative_path = video_file.relative_to(raw_data_path)
                output_json = landmarks_path / relative_path.with_suffix('.json')
                output_json.parent.mkdir(parents=True, exist_ok=True)

                logger.info(f"Processing: {relative_path}")

                # Process video
                results = self.process_video(str(video_file))

                # Save landmarks as JSON
                self.save_landmarks_json(results, str(output_json))

                processed_count += 1
                total_frames += results["total_frames"]

                logger.info(f"✅ Saved: {output_json} ({results['total_frames']} frames)")

            except Exception as e:
                logger.error(f"❌ Failed to process {video_file}: {e}")
                error_count += 1

        logger.info(f"\n{'='*60}")
        logger.info("BATCH PROCESSING COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total videos found: {len(video_files)}")
        logger.info(f"Successfully processed: {processed_count}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"Total frames processed: {total_frames}")
        logger.info(f"{'='*60}")

        return {
            "total_videos": len(video_files),
            "processed_videos": processed_count,
            "errors": error_count,
            "total_frames": total_frames
        }


def main():
    """
    Batch process all videos in data/raw/ and save landmarks to data/landmarks/
    """
    # Paths
    data_raw_path = Path(__file__).parent.parent.parent / "data" / "raw"
    data_landmarks_path = Path(__file__).parent.parent.parent / "data" / "landmarks"

    logger.info("Starting batch landmark extraction...")
    logger.info(f"Input directory: {data_raw_path}")
    logger.info(f"Output directory: {data_landmarks_path}")

    # Extract landmarks
    extractor = LandmarkExtractor(confidence_threshold=0.5)

    try:
        results = extractor.process_all_videos(str(data_raw_path), str(data_landmarks_path))

        print("\n" + "="*60)
        print("BATCH LANDMARK EXTRACTION COMPLETE")
        print("="*60)
        print(f"Total videos:     {results['total_videos']}")
        print(f"Processed:        {results['processed_videos']}")
        print(f"Errors:           {results['errors']}")
        print(f"Total frames:     {results['total_frames']}")
        print(f"Output directory: {data_landmarks_path}")
        print("="*60)

    finally:
        extractor.close()


if __name__ == "__main__":
    main()

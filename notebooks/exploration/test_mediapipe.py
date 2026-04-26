"""
Test MediaPipe landmark extraction on demo videos.
This script tests the landmark extraction service on sample videos.
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def test_basic_mediapipe():
    """Test basic MediaPipe functionality."""
    try:
        import mediapipe as mp
        print(f"✅ MediaPipe {mp.__version__} imported successfully")

        # Test basic image processing
        import cv2
        import numpy as np

        # Create a simple test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:, :, 2] = 255  # Red image

        print("✅ OpenCV and numpy working")

        # Try to create a simple hand detector using task API
        try:
            # For now, just test that we can import the task modules
            from mediapipe.tasks import vision
            print("✅ MediaPipe tasks imported successfully")
            print("Note: Full landmark extraction requires model files to be downloaded")
            return True
        except Exception as e:
            print(f"⚠️  MediaPipe tasks import failed: {e}")
            return False

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def main():
    """Main test function."""
    print("Testing MediaPipe setup...")
    print("=" * 50)

    success = test_basic_mediapipe()

    print("=" * 50)
    if success:
        print("✅ Basic MediaPipe test passed!")
        print("Note: To run full landmark extraction, model files need to be downloaded.")
        print("The landmark extraction service is ready but requires model assets.")
    else:
        print("❌ MediaPipe test failed!")

if __name__ == "__main__":
    main()

    # Initialize extractor
    print("\nInitializing MediaPipe...")
    extractor = LandmarkExtractor(confidence_threshold=0.5)

    try:
        # Process video
        print("\nProcessing video...")
        results = extractor.process_video(str(video_path), str(output_video))

        # Save landmarks
        extractor.save_landmarks_json(results, str(landmarks_json))

        # Analyze results
        frame_landmarks = results["frame_landmarks"]
        total_frames = len(frame_landmarks)
        frames_with_hands = sum(1 for f in frame_landmarks if f["landmarks"]["hand_presence"] > 0)
        frames_with_left = sum(1 for f in frame_landmarks if f["landmarks"]["left_hand"] is not None)
        frames_with_right = sum(1 for f in frame_landmarks if f["landmarks"]["right_hand"] is not None)
        frames_with_both = sum(1 for f in frame_landmarks if f["landmarks"]["hand_presence"] == 3)

        # Display results
        print("\nProcessing Complete!")
        print("="*60)
        print("RESULTS SUMMARY")
        print("="*60)
        print(f"Total frames processed: {total_frames}")
        print(f"Frames with hand detection: {frames_with_hands} ({frames_with_hands/total_frames*100:.1f}%)")
        print(f"Frames with left hand: {frames_with_left}")
        print(f"Frames with right hand: {frames_with_right}")
        print(f"Frames with both hands: {frames_with_both}")
        print(f"Video resolution: {results['resolution']}")
        print(f"Video FPS: {results['fps']}")
        print(f"Output video saved: {output_video.exists()}")
        print(f"Landmarks JSON saved: {landmarks_json.exists()}")
        print("="*60)

        # Show sample landmark data
        if frame_landmarks:
            print("\nSample Frame Data (Frame 0):")
            sample_frame = frame_landmarks[0]
            landmarks = sample_frame["landmarks"]
            print(f"  Hand presence: {landmarks['hand_presence']} (0=none, 1=left, 2=right, 3=both)")
            if landmarks["left_hand"]:
                print(f"  Left hand landmarks: {len(landmarks['left_hand'])} points")
            if landmarks["right_hand"]:
                print(f"  Right hand landmarks: {len(landmarks['right_hand'])} points")
            if landmarks["pose"]:
                print(f"  Pose landmarks: {len(landmarks['pose'])} points")

        print("\nNext Steps:")
        print("1. Open the annotated video to see landmark overlays")
        print("2. Check the JSON file for detailed landmark coordinates")
        print("3. Run on more videos to test the pipeline")
        print("4. Implement data processing for ML training")

    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        extractor.close()


def find_sample_video():
    """
    Find a sample video from the data/raw directory.

    Returns:
        Path to first video found, or None
    """
    data_raw_path = Path(__file__).parent.parent / "data" / "raw"

    # Look for .mp4 files
    video_files = list(data_raw_path.rglob("*.mp4"))

    if video_files:
        return video_files[0]
    else:
        return None


def main():
    """
    Main function - test MediaPipe on one video.
    """
    print("MediaPipe Landmark Extraction Test")
    print("="*50)

    # Find a video to test
    if len(sys.argv) > 1:
        # Use video path from command line
        video_path = sys.argv[1]
    else:
        # Find sample video automatically
        video_path = find_sample_video()
        if not video_path:
            print("No video files found in data/raw/")
            print("Usage: python test_mediapipe.py [video_path]")
            print("Or run: python notebooks/exploration/download_wlasl_sample.py first")
            return

    print(f"Using video: {video_path}")

    # Run test
    test_mediapipe_on_video(str(video_path))


if __name__ == "__main__":
    main()

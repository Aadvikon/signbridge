"""
Test Prediction Pipeline
Load a video, extract landmarks, and test the prediction service.
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from services.landmark_extraction import LandmarkExtractor
from services.predictor import SignPredictor
import json


def test_prediction_pipeline(video_path: str):
    """
    Complete prediction pipeline test.

    Args:
        video_path: Path to video file to test
    """
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        return

    print("Testing SignBridge Prediction Pipeline")
    print("=" * 50)
    print(f"Input video: {video_path}")
    print(f"File size: {video_path.stat().st_size / 1024:.1f} KB")
    print()

    try:
        # Step 1: Extract landmarks
        print("Step 1: Extracting landmarks...")
        extractor = LandmarkExtractor(confidence_threshold=0.5)

        results = extractor.process_video(str(video_path))
        print(f"✅ Extracted landmarks from {results['total_frames']} frames")
        print(f"   Video resolution: {results['resolution']}")
        print(f"   FPS: {results['fps']}")
        print()

        # Step 2: Save landmarks temporarily for prediction
        temp_json = video_path.parent / f"{video_path.stem}_temp.json"
        extractor.save_landmarks_json(results, str(temp_json))
        print(f"✅ Saved landmarks to: {temp_json}")
        print()

        # Step 3: Make prediction
        print("Step 3: Making prediction...")
        try:
            predictor = SignPredictor()

            prediction = predictor.predict_from_json(str(temp_json))

            print("🎯 PREDICTION RESULT:")
            print(f"   Sign: {prediction['sign']}")
            print(f"   Confidence: {prediction['confidence']:.1f}%")
            print(f"   Class Index: {prediction['class_index']}")
            print()
            print("   All Probabilities:")
            for sign, prob in sorted(prediction['all_probabilities'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(".1f"
            print()

        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            print("Note: This may be because the model hasn't been trained yet.")
            print("Run the trainer first: python backend/services/trainer.py")
            print()

        # Cleanup
        if temp_json.exists():
            temp_json.unlink()
            print(f"🧹 Cleaned up temporary file: {temp_json}")

        extractor.close()

    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")


def main():
    """
    Main test function.
    """
    # Find a test video
    data_raw_path = Path(__file__).parent.parent.parent / "data" / "raw"

    # Look for test video first, then any mp4 file
    test_video = data_raw_path / "HELLO" / "test_video.mp4"
    if not test_video.exists():
        # Find any mp4 file
        import glob
        mp4_files = list(data_raw_path.rglob("*.mp4"))
        if mp4_files:
            test_video = mp4_files[0]
        else:
            print("❌ No video files found in data/raw/")
            return

    print(f"Found test video: {test_video}")
    print()

    # Run prediction test
    test_prediction_pipeline(str(test_video))

    print("=" * 50)
    print("Pipeline test complete!")


if __name__ == "__main__":
    main()
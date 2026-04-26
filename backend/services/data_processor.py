"""
Data Processor Service
Converts landmark JSON files into numpy arrays ready for ML training.
Pads sequences to fixed length and creates train/val/test splits.
"""

import numpy as np
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes landmark JSON files into training-ready numpy arrays.
    """

    def __init__(self, sequence_length: int = 30):
        """
        Initialize data processor.

        Args:
            sequence_length: Fixed length to pad/truncate all sequences to
        """
        self.sequence_length = sequence_length
        logger.info(f"Initialized DataProcessor (sequence_length: {sequence_length})")

    def load_landmark_data(self, landmarks_path: str) -> Dict[str, List]:
        """
        Load all landmark JSON files from data/landmarks/.

        Args:
            landmarks_path: Path to data/landmarks/ directory

        Returns:
            Dictionary mapping sign names to lists of landmark sequences
        """
        landmarks_path = Path(landmarks_path)
        if not landmarks_path.exists():
            raise FileNotFoundError(f"Landmarks path not found: {landmarks_path}")

        # Find all JSON files
        json_files = list(landmarks_path.rglob("*.json"))
        if not json_files:
            logger.warning(f"No JSON files found in {landmarks_path}")
            return {}

        logger.info(f"Found {len(json_files)} landmark JSON files")

        # Group by sign (directory name)
        sign_data = {}

        for json_file in json_files:
            try:
                # Extract sign name from path (parent directory name)
                sign_name = json_file.parent.name

                # Load JSON data
                with open(json_file, 'r') as f:
                    data = json.load(f)

                # Extract landmark sequence
                frame_landmarks = data["frame_landmarks"]
                sequence = self._extract_sequence_from_frames(frame_landmarks)

                if sign_name not in sign_data:
                    sign_data[sign_name] = []

                sign_data[sign_name].append(sequence)
                logger.info(f"Loaded: {json_file.relative_to(landmarks_path)} ({len(sequence)} frames)")

            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")

        # Log summary
        total_sequences = sum(len(sequences) for sequences in sign_data.values())
        logger.info(f"Loaded {total_sequences} sequences for {len(sign_data)} signs")

        return sign_data

    def _extract_sequence_from_frames(self, frame_landmarks: List[Dict]) -> List[List[float]]:
        """
        Extract landmark sequence from frame data.

        Args:
            frame_landmarks: List of frame landmark dictionaries

        Returns:
            List of flattened landmark vectors for each frame
        """
        sequence = []

        for frame_data in frame_landmarks:
            landmarks = frame_data["landmarks"]

            # Flatten all landmarks into single vector
            frame_vector = []

            # Add hand landmarks (left and right)
            for hand_key in ["left_hand", "right_hand"]:
                hand_data = landmarks.get(hand_key)
                if hand_data:
                    # Flatten 21 landmarks * 4 values each (x, y, z, confidence)
                    for landmark in hand_data:
                        frame_vector.extend(landmark)
                else:
                    # Pad with zeros if hand not detected
                    frame_vector.extend([0.0] * (21 * 4))

            # Add pose landmarks
            pose_data = landmarks.get("pose")
            if pose_data:
                # Flatten pose landmarks
                for landmark in pose_data:
                    frame_vector.extend(landmark)
            else:
                # Pad with zeros (assuming 12 upper body landmarks)
                frame_vector.extend([0.0] * (12 * 4))

            sequence.append(frame_vector)

        return sequence

    def pad_sequences(self, sequences: List[List], max_length: Optional[int] = None) -> np.ndarray:
        """
        Pad or truncate sequences to fixed length.

        Args:
            sequences: List of landmark sequences
            max_length: Maximum sequence length (default: self.sequence_length)

        Returns:
            Numpy array of shape (num_sequences, max_length, num_features)
        """
        if max_length is None:
            max_length = self.sequence_length

        # Find feature dimension from first sequence
        if not sequences:
            return np.array([])

        feature_dim = len(sequences[0][0]) if sequences[0] else 0

        # Pad/truncate each sequence
        padded_sequences = []
        for seq in sequences:
            if len(seq) > max_length:
                # Truncate
                padded_seq = seq[:max_length]
            else:
                # Pad with zeros
                padding_needed = max_length - len(seq)
                if padding_needed > 0:
                    # Create padding frames (copy last frame or zeros)
                    if seq:
                        padding_frame = seq[-1]  # Repeat last frame
                    else:
                        padding_frame = [0.0] * feature_dim
                    padding = [padding_frame] * padding_needed
                    padded_seq = seq + padding
                else:
                    padded_seq = seq

            padded_sequences.append(padded_seq)

        # Convert to numpy array
        result = np.array(padded_sequences)
        logger.info(f"Padded sequences: {result.shape} (sequences x frames x features)")

        return result

    def create_dataset(self, sign_data: Dict[str, List], processed_path: str) -> Dict:
        """
        Create complete dataset from sign data.

        Args:
            sign_data: Dictionary mapping signs to landmark sequences
            processed_path: Path to save processed data

        Returns:
            Dataset statistics
        """
        processed_path = Path(processed_path)
        processed_path.mkdir(parents=True, exist_ok=True)

        # Collect all sequences and labels
        all_sequences = []
        all_labels = []
        sign_to_index = {}

        # Create sign vocabulary
        for i, sign_name in enumerate(sorted(sign_data.keys())):
            sign_to_index[sign_name] = i

        # Process each sign
        for sign_name, sequences in sign_data.items():
            sign_index = sign_to_index[sign_name]

            # Pad sequences for this sign
            padded_sequences = self.pad_sequences(sequences)

            all_sequences.extend(padded_sequences)
            all_labels.extend([sign_index] * len(padded_sequences))

            logger.info(f"Processed {sign_name}: {len(sequences)} sequences -> {padded_sequences.shape}")

        # Convert to numpy arrays
        X = np.array(all_sequences)
        y = np.array(all_labels)

        # Save arrays
        x_path = processed_path / "X.npy"
        y_path = processed_path / "y.npy"
        vocab_path = processed_path / "sign_vocabulary.json"

        np.save(x_path, X)
        np.save(y_path, y)

        # Save vocabulary
        vocabulary = {
            "sign_to_index": sign_to_index,
            "index_to_sign": {v: k for k, v in sign_to_index.items()},
            "num_classes": len(sign_to_index)
        }

        with open(vocab_path, 'w') as f:
            json.dump(vocabulary, f, indent=2)

        logger.info(f"Saved dataset to {processed_path}")
        logger.info(f"X.npy: {X.shape} (sequences x frames x features)")
        logger.info(f"y.npy: {y.shape} (sequence labels)")
        logger.info(f"Vocabulary: {len(sign_to_index)} signs")

        return {
            "X_shape": X.shape,
            "y_shape": y.shape,
            "num_classes": len(sign_to_index),
            "signs": list(sign_to_index.keys()),
            "vocabulary_path": str(vocab_path),
            "X_path": str(x_path),
            "y_path": str(y_path)
        }


def main():
    """
    Process all landmark JSON files and create training dataset.
    """
    # Paths
    data_landmarks_path = Path(__file__).parent.parent.parent / "data" / "landmarks"
    data_processed_path = Path(__file__).parent.parent.parent / "data" / "processed"

    logger.info("Starting data processing...")
    logger.info(f"Input directory: {data_landmarks_path}")
    logger.info(f"Output directory: {data_processed_path}")

    # Process data
    processor = DataProcessor(sequence_length=30)

    try:
        # Load landmark data
        sign_data = processor.load_landmark_data(str(data_landmarks_path))

        if not sign_data:
            logger.error("No landmark data found!")
            return

        # Create dataset
        stats = processor.create_dataset(sign_data, str(data_processed_path))

        print("\n" + "="*60)
        print("DATA PROCESSING COMPLETE")
        print("="*60)
        print(f"Dataset shape:    {stats['X_shape']}")
        print(f"Labels shape:     {stats['y_shape']}")
        print(f"Number of signs:  {stats['num_classes']}")
        print(f"Signs:            {', '.join(stats['signs'])}")
        print(f"X.npy saved:      {stats['X_path']}")
        print(f"y.npy saved:      {stats['y_path']}")
        print(f"Vocabulary:       {stats['vocabulary_path']}")
        print("="*60)

    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
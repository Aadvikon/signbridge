"""
Prediction Service
Loads trained model and makes sign predictions from landmark sequences.
"""

import torch
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SignPredictor:
    """
    Predicts sign language gestures from landmark sequences using trained model.
    """

    def __init__(self, model_path: str = None, vocab_path: str = None):
        """
        Initialize the predictor.

        Args:
            model_path: Path to trained model file
            vocab_path: Path to vocabulary JSON file
        """
        if model_path is None:
            model_path = Path(__file__).parent.parent / "models" / "trained" / "signbridge_v1.pth"
        if vocab_path is None:
            vocab_path = Path(__file__).parent.parent / "data" / "processed" / "sign_vocabulary.json"

        self.model_path = Path(model_path)
        self.vocab_path = Path(vocab_path)
        self.model = None
        self.vocab = None
        self._model_loaded = False
        self._vocab_loaded = False

        logger.info(f"Initialized SignPredictor with model_path={self.model_path} and vocab_path={self.vocab_path}")

    def load_model(self):
        """Load the trained PyTorch model."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        from models.lstm_model import SignLanguageLSTM
        self.model = SignLanguageLSTM.load_model(str(self.model_path))
        self.model.eval()  # Set to evaluation mode
        self._model_loaded = True
        logger.info(f"Model loaded from: {self.model_path}")

    def load_vocabulary(self):
        """Load the sign vocabulary."""
        if not self.vocab_path.exists():
            raise FileNotFoundError(f"Vocabulary file not found: {self.vocab_path}")

        with open(self.vocab_path, 'r') as f:
            self.vocab = json.load(f)

        self._vocab_loaded = True
        logger.info(f"Vocabulary loaded: {self.vocab.get('num_classes', 'unknown')} signs")

    def load_resources(self):
        """Load model and vocabulary resources if not already loaded."""
        if not self._vocab_loaded:
            self.load_vocabulary()
        if not self._model_loaded:
            self.load_model()

    def preprocess_sequence(self, landmarks: List[List[float]], sequence_length: int = 30) -> torch.Tensor:
        """
        Preprocess landmark sequence for prediction.

        Args:
            landmarks: List of landmark frames
            sequence_length: Expected sequence length

        Returns:
            Preprocessed torch tensor ready for model input
        """
        # Convert to numpy array
        sequence = np.array(landmarks)

        # Ensure correct shape (should already be processed by data_processor)
        if sequence.ndim == 2:
            sequence = sequence.reshape(1, sequence.shape[0], sequence.shape[1])

        # Pad or truncate to expected length
        current_length = sequence.shape[1]

        if current_length > sequence_length:
            # Truncate
            sequence = sequence[:, :sequence_length, :]
        elif current_length < sequence_length:
            # Pad with zeros
            padding_needed = sequence_length - current_length
            padding = np.zeros((1, padding_needed, sequence.shape[2]))
            sequence = np.concatenate([sequence, padding], axis=1)

        # Convert to torch tensor
        return torch.FloatTensor(sequence)

    def predict(self, landmarks: Union[List[List[float]], np.ndarray, torch.Tensor]) -> Dict:
        """
        Predict sign from landmark sequence.

        Args:
            landmarks: Landmark sequence (list of frames, numpy array, or torch tensor)

        Returns:
            Dictionary with prediction results
        """
        self.load_resources()

        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        # Preprocess input
        if isinstance(landmarks, (list, np.ndarray)):
            processed_input = self.preprocess_sequence(landmarks)
        elif isinstance(landmarks, torch.Tensor):
            processed_input = landmarks
        else:
            raise ValueError("Unsupported input type for landmarks")

        # Move to device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        processed_input = processed_input.to(device)
        self.model.to(device)

        # Make prediction
        with torch.no_grad():
            self.model.eval()
            outputs = self.model(processed_input)
            probabilities = torch.softmax(outputs, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item() * 100

        # Get sign name
        sign_name = self.vocab['index_to_sign'][str(predicted_class)]

        # Get all probabilities
        all_probs = probabilities[0].cpu().numpy()
        all_probabilities = {
            self.vocab['index_to_sign'][str(i)]: round(float(prob * 100), 1)
            for i, prob in enumerate(all_probs)
        }

        result = {
            "sign": sign_name,
            "confidence": round(confidence, 1),
            "class_index": int(predicted_class),
            "all_probabilities": all_probabilities
        }

        logger.info(f"Prediction: {sign_name} ({confidence:.1f}% confidence)")
        return result

    def predict_from_json(self, json_path: str) -> Dict:
        """
        Predict sign from landmark JSON file.

        Args:
            json_path: Path to landmark JSON file

        Returns:
            Dictionary with prediction results
        """
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        # Load landmarks from JSON
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Extract landmark sequence (same as data_processor)
        frame_landmarks = data["frame_landmarks"]
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

        # Make prediction
        return self.predict(sequence)


def main():
    """
    Example usage of SignPredictor.
    """
    try:
        predictor = SignPredictor()

        # Example: predict from a landmark JSON file
        # This would be used in production
        print("SignPredictor initialized successfully!")
        print(f"Model: {predictor.model_path}")
        print(f"Vocabulary: {predictor.vocab_path}")
        print(f"Number of signs: {predictor.vocab['num_classes']}")

    except Exception as e:
        print(f"Failed to initialize predictor: {e}")


if __name__ == "__main__":
    main()
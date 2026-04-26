"""
Model Trainer Service
Loads processed data and trains the LSTM model for sign recognition.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import json
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Trains the SignBridge LSTM model on processed landmark data.
    """

    def __init__(self, processed_data_path: str = None, models_path: str = None):
        """
        Initialize the trainer.

        Args:
            processed_data_path: Path to processed data directory
            models_path: Path to save trained models
        """
        if processed_data_path is None:
            processed_data_path = Path(__file__).parent.parent.parent / "data" / "processed"
        if models_path is None:
            models_path = Path(__file__).parent.parent.parent / "models" / "trained"

        self.processed_data_path = Path(processed_data_path)
        self.models_path = Path(models_path)
        self.models_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized ModelTrainer")
        logger.info(f"Data path: {self.processed_data_path}")
        logger.info(f"Models path: {self.models_path}")

    def load_data(self):
        """
        Load X.npy and y.npy from processed data directory.

        Returns:
            Tuple of (X, y) numpy arrays
        """
        x_path = self.processed_data_path / "X.npy"
        y_path = self.processed_data_path / "y.npy"

        if not x_path.exists():
            raise FileNotFoundError(f"X.npy not found: {x_path}")
        if not y_path.exists():
            raise FileNotFoundError(f"y.npy not found: {y_path}")

        X = np.load(x_path)
        y = np.load(y_path)

        logger.info(f"Loaded data: X shape {X.shape}, y shape {y.shape}")
        logger.info(f"Number of classes: {len(np.unique(y))}")

        return X, y

    def load_vocabulary(self):
        """
        Load sign vocabulary from processed data.

        Returns:
            Dictionary with vocabulary information
        """
        vocab_path = self.processed_data_path / "sign_vocabulary.json"

        if not vocab_path.exists():
            raise FileNotFoundError(f"Vocabulary not found: {vocab_path}")

        with open(vocab_path, 'r') as f:
            vocab = json.load(f)

        logger.info(f"Loaded vocabulary: {vocab['num_classes']} signs")
        return vocab

    def split_data(self, X, y, test_size: float = 0.2, random_state: int = 42):
        """
        Split data into training and validation sets.

        Args:
            X: Input sequences
            y: Labels
            test_size: Fraction for validation
            random_state: Random seed

        Returns:
            Tuple of (X_train, X_val, y_train, y_val)
        """
        # For very small datasets, ensure we have at least 1 sample per split
        if len(X) < 5:
            # If we have very few samples, use them all for training
            logger.warning(f"Very small dataset ({len(X)} samples). Using all data for training.")
            return X, X[:0], y, y[:0]  # Empty validation set

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        logger.info(f"Data split: Train {X_train.shape}, Val {X_val.shape}")
        return X_train, X_val, y_train, y_val

    def train_model(self, model, X_train, y_train, X_val, y_val,
                   epochs: int = 50, batch_size: int = 32, learning_rate: float = 0.001):
        """
        Train the model and return training history.

        Args:
            model: PyTorch model to train
            X_train: Training input sequences
            y_train: Training labels
            X_val: Validation input sequences
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for optimizer

        Returns:
            Training history dictionary
        """
        logger.info(f"Starting training for {epochs} epochs (batch_size: {batch_size}, lr: {learning_rate})")

        # Convert to PyTorch tensors
        X_train_tensor = torch.FloatTensor(X_train)
        y_train_tensor = torch.LongTensor(y_train)
        X_val_tensor = torch.FloatTensor(X_val) if len(X_val) > 0 else None
        y_val_tensor = torch.LongTensor(y_val) if len(y_val) > 0 else None

        # Create data loaders
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Setup optimizer and loss function
        optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()

        # Move model to device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model.to(device)

        history = {
            'accuracy': [],
            'loss': [],
            'val_accuracy': [],
            'val_loss': []
        }

        for epoch in range(epochs):
            model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0

            # Training loop
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)

                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                train_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                train_total += batch_y.size(0)
                train_correct += (predicted == batch_y).sum().item()

            # Calculate training metrics
            train_accuracy = 100 * train_correct / train_total
            train_loss = train_loss / len(train_loader)

            # Validation
            val_accuracy = 0.0
            val_loss = 0.0

            if X_val_tensor is not None and len(X_val_tensor) > 0:
                model.eval()
                with torch.no_grad():
                    X_val_tensor = X_val_tensor.to(device)
                    y_val_tensor = y_val_tensor.to(device)

                    val_outputs = model(X_val_tensor)
                    val_loss = criterion(val_outputs, y_val_tensor).item()
                    _, val_predicted = torch.max(val_outputs.data, 1)
                    val_correct = (val_predicted == y_val_tensor).sum().item()
                    val_accuracy = 100 * val_correct / y_val_tensor.size(0)

            # Store metrics
            history['accuracy'].append(train_accuracy)
            history['loss'].append(train_loss)
            history['val_accuracy'].append(val_accuracy)
            history['val_loss'].append(val_loss)

            logger.info(f"Epoch {epoch+1:2d}: Train Acc {train_accuracy:5.2f}%, Val Acc {val_accuracy:5.2f}%")

        return history

    def save_training_history(self, history: dict, filepath: str):
        """
        Save training history to JSON file.

        Args:
            history: Training history dictionary
            filepath: Path to save history
        """
        # Convert numpy values to native Python types
        serializable_history = {}
        for key, values in history.items():
            if isinstance(values, (list, np.ndarray)):
                serializable_history[key] = [float(v) for v in values]
            else:
                serializable_history[key] = float(values)

        with open(filepath, 'w') as f:
            json.dump(serializable_history, f, indent=2)

        logger.info(f"Training history saved to: {filepath}")

    def run_training_pipeline(self, epochs: int = 50):
        """
        Complete training pipeline: load data, train model, save results.

        Args:
            epochs: Number of training epochs

        Returns:
            Dictionary with training results
        """
        try:
            # Load data and vocabulary
            X, y = self.load_data()
            vocab = self.load_vocabulary()

            # Split data
            X_train, X_val, y_train, y_val = self.split_data(X, y)

            # Import and create model
            from backend.models.lstm_model import create_signbridge_model

            num_classes = vocab['num_classes']
            sequence_length, num_features = X.shape[1], X.shape[2]

            model = create_signbridge_model(
                num_classes=num_classes,
                sequence_length=sequence_length,
                num_features=num_features
            )

            # Train model
            history = self.train_model(model, X_train, y_train, X_val, y_val, epochs=epochs)

            # Save model and history
            model_path = self.models_path / "signbridge_v1.pth"
            history_path = self.models_path / "history.json"

            model.save_model(str(model_path))
            self.save_training_history(history, str(history_path))

            # Get final accuracies
            final_train_acc = history['accuracy'][-1] if history['accuracy'] else 0
            final_val_acc = history['val_accuracy'][-1] if history['val_accuracy'] else 0

            logger.info(f"Final training accuracy: {final_train_acc:.2f}")
            logger.info(f"Final validation accuracy: {final_val_acc:.2f}")
            print("\n" + "="*60)
            print("TRAINING COMPLETE")
            print("="*60)
            print(f"Final training accuracy: {final_train_acc:.2f}")
            print(f"Final validation accuracy: {final_val_acc:.2f}")
            print(f"Model saved:     {model_path}")
            print(f"History saved:   {history_path}")
            print("="*60)

            return {
                "model_path": str(model_path),
                "history_path": str(history_path),
                "final_train_accuracy": final_train_acc,
                "final_val_accuracy": final_val_acc,
                "epochs": epochs,
                "num_classes": num_classes
            }

        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise


def main():
    """
    Run the complete training pipeline.
    """
    trainer = ModelTrainer()
    results = trainer.run_training_pipeline(epochs=50)


if __name__ == "__main__":
    main()
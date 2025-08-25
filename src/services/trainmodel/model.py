"""
Model Fine-Tuning Module
Handles preprocessing, sequence generation, and fine-tuning of LSTM models
for stock price prediction using new training data.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam


class ModelFineTuning:
    """
    Fine-tunes a pre-trained LSTM model or trains a new one from scratch
    using the latest stock price data.

    Attributes:
        training_data_path (str | Path): Path to CSV file with training data.
        pre_trained_model_path (str | Path): Path to save/load the Keras model.
        look_back (int): Number of previous days used for sequence generation.
    """

    def __init__(self, training_data_path: str, pre_trained_model_path: str, look_back: int = 15):
        self.training_data_path = training_data_path
        self.pre_trained_model_path = pre_trained_model_path
        self.look_back = look_back

        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.train_data: np.ndarray | None = None
        self.test_data: np.ndarray | None = None
        self.model: Sequential | None = None

    # Data Preprocessing
    def data_frame_training(self) -> None:
        """Loads CSV data, scales 'Close' prices, and splits into train/test sets."""
        df = pd.read_csv(self.training_data_path, index_col=0)
        df['Date'] = pd.to_datetime(df.index)
        scaled = self.scaler.fit_transform(df['Close'].values.reshape(-1, 1))
        split_idx = int(len(scaled) * 0.7)
        self.train_data, self.test_data = scaled[:split_idx], scaled[split_idx:]

    def generate_sequences(self, dataset: np.ndarray, look_back: int = 15) -> tuple[np.ndarray, np.ndarray]:
        """
        Generates sequences for LSTM input.

        Args:
            dataset (np.ndarray): Array of scaled prices.
            look_back (int): Number of previous days to use for prediction.

        Returns:
            Tuple of arrays: (X sequences, y labels)
        """
        X, y = [], []
        for i in range(len(dataset) - look_back):
            X.append(dataset[i:i + look_back])
            y.append(dataset[i + look_back])
        return np.array(X), np.array(y)

    # Model Handling
    def load_pre_trained_model(self) -> None:
        """Loads a pre-trained model from file if it exists; otherwise sets model to None."""
        try:
            self.model = load_model(self.pre_trained_model_path)
        except Exception:
            self.model = None

    def fine_tune(self) -> None:
        """
        Fine-tunes the pre-trained model or trains a new LSTM from scratch
        using the training data.
        """
        if self.train_data is None or self.test_data is None:
            raise ValueError("Training and test data must be initialized by calling data_frame_training() first.")

        x_train, y_train = self.generate_sequences(self.train_data, self.look_back)
        x_test, y_test = self.generate_sequences(self.test_data, self.look_back)

        # Reshape for LSTM input: (samples, time_steps, features)
        x_train = np.reshape(x_train, (x_train.shape[0], self.look_back, 1))
        x_test = np.reshape(x_test, (x_test.shape[0], self.look_back, 1))

        if self.model is None:
            # Create new LSTM model if no pre-trained model exists
            self.model = Sequential([
                LSTM(20, input_shape=(self.look_back, 1)),
                Dense(1)
            ])

        self.model.compile(optimizer=Adam(learning_rate=0.0001), loss='mean_squared_error', metrics=['mae'])

        # Train or fine-tune the model
        self.model.fit(x_train, y_train, epochs=5, batch_size=32, verbose=2)

        # Save updated model
        self.model.save(self.pre_trained_model_path)
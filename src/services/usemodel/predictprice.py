"""
Model Predictor Module
Handles preprocessing and prediction of stock prices using a pre-loaded Keras LSTM model.
Also provides Redis caching utilities for storing and retrieving models.
"""

import os
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Model

# Environment Configuration
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Model Predictor Class
class ModelPredictor:
    """
    Generates stock price predictions using a pre-loaded Keras LSTM model.

    Attributes:
        data_source (Union[str, Path, pd.DataFrame]): CSV file path or DataFrame containing historical stock data.
        model (keras.Model): Pre-loaded Keras model for prediction.
    """

    def __init__(self, data_source: Union[str, Path, pd.DataFrame], model: Model):
        self.data_source = data_source
        self.model = model

    def _generate_prediction(self) -> float:
        """
        Generates a stock price prediction based on the last 80 days of closing prices.

        Returns:
            float: Predicted stock price.

        Raises:
            FileNotFoundError: If CSV file is missing.
            ValueError: If there is insufficient data for prediction.
        """
        # Load data
        if isinstance(self.data_source, pd.DataFrame):
            data = self.data_source
        else:
            try:
                data = pd.read_csv(self.data_source, index_col=0)
            except FileNotFoundError:
                raise FileNotFoundError(f"Data file not found at {self.data_source}")

        # Ensure 'Date' column exists
        if 'Date' not in data.columns and data.index.name != 'Date':
            data['Date'] = pd.to_datetime(data.index)

        # Scale 'Close' prices
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

        # Check if enough data is available
        time_steps = 80
        if len(scaled_data) < time_steps:
            raise ValueError(
                f"Insufficient data for prediction. Required: {time_steps}, Found: {len(scaled_data)}"
            )

        # Prepare last sequence for prediction
        last_sequence = scaled_data[-time_steps:]
        reshaped_sequence = np.reshape(last_sequence, (1, time_steps, 1))

        # Generate prediction and inverse scale
        prediction_scaled = self.model.predict(reshaped_sequence)
        predicted_value = scaler.inverse_transform(prediction_scaled)[0, 0]
        return predicted_value

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

class ModelPredictor:
    """
    Handles price prediction using a pre-loaded Keras model.
    """
    def __init__(self, data_path_or_df, model):
        """
        Initializes the predictor with a data path/DataFrame and a pre-loaded model object.

        Args:
            data_path_or_df (pathlib.Path, str, or pd.DataFrame): The path to the CSV data file or a pre-loaded DataFrame.
            model (keras.Model): The pre-loaded Keras model object passed from the main app.
        """
        self.data_source = data_path_or_df
        self.model = model
        
    def _generate_prediction(self):
        """
        Loads data, preprocesses it, and generates a price prediction.

        Returns:
            float: The predicted stock price.
        """
        try:
            if isinstance(self.data_source, pd.DataFrame):
                data = self.data_source
            else:
                data = pd.read_csv(self.data_source, index_col=0)
            
            if 'Date' not in data.columns and data.index.name != 'Date':
                 data['Date'] = pd.to_datetime(data.index)

        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found at {self.data_source}")

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))
        
        time_steps = 80

        if len(scaled_data) < time_steps:
            raise ValueError(f"Insufficient data for prediction. Need at least {time_steps} records, but found {len(scaled_data)}.")

        last_sequence = scaled_data[-time_steps:]
        reshaped_data = np.reshape(last_sequence, (1, time_steps, 1))
        
        prediction_scaled = self.model.predict(reshaped_data)
        predicted_value = scaler.inverse_transform(prediction_scaled)[0, 0]
        
        return predicted_value
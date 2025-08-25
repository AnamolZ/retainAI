import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import sys
import redis
import tempfile
from keras.models import load_model

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

# Redis connection and helper functions
r = redis.Redis(host="localhost", port=6379, db=0)

def set_modelCache(model, key_name="keras_model"):
    fd, path = tempfile.mkstemp(suffix=".h5")
    os.close(fd)
    try:
        model.save(path)
        with open(path, "rb") as f:
            r.set(key_name, f.read())
        print(f"Model saved in Redis under key '{key_name}'")
    finally:
        os.remove(path)

def get_modelCache(key_name="keras_model"):
    data = r.get(key_name)
    if not data:
        raise ValueError(f"No model found in Redis with key '{key_name}'")
    fd, path = tempfile.mkstemp(suffix=".h5")
    os.close(fd)
    try:
        with open(path, "wb") as f:
            f.write(data)
        model = load_model(path, compile=False)
        print(f"Model loaded from Redis (key: {key_name})")
        return model
    finally:
        os.remove(path)

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    sys.path.append(str(PROJECT_ROOT))
    
    from src.services.database.postgresbase import PostgresDB

    Postgres_base = PostgresDB()

    training_data_df = Postgres_base.fetch_data('SELECT * FROM "dataPriceNVDA";')
    model_from_redis = get_modelCache("NAS_NVDA")
    
    model_predictor = ModelPredictor(training_data_df, model_from_redis)

    prediction = model_predictor._generate_prediction()
    print(f"Predicted Value for NVDA: {prediction}")
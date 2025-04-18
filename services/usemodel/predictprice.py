from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import os
import tensorflow as tf

class ModelPredictor:
    def __init__(self, data_path, model_path):
        self.data_path = data_path
        self.model_path = model_path
        self.model = load_model(self.model_path)
        self.predicted_value = self._generate_prediction()

    def _generate_prediction(self):
        data = pd.read_csv(self.data_path, index_col=0)
        data['Date'] = pd.to_datetime(data.index)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

        time_steps = 80
        if len(scaled_data) >= time_steps:
            reshaped_data = np.reshape(scaled_data[-time_steps:], (1, time_steps, 1))
        else:
            raise ValueError("Insufficient data to make a prediction with the required time steps.")
        
        prediction = self.model.predict(reshaped_data)
        predicted_value = scaler.inverse_transform(prediction)[0, 0]

        return predicted_value

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam

class ModelFineTuning:
    def __init__(self, training_data_path: str, pre_trained_model_path: str, look_back: int = 15):
        self.training_data_path = training_data_path
        self.look_back = look_back
        self.pre_trained_model_path = pre_trained_model_path
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.train_data = None
        self.test_data = None
        self.model = None

    def data_frame_training(self):
        training_data_frame = pd.read_csv(self.training_data_path, index_col=0)
        training_data_frame['Date'] = pd.to_datetime(training_data_frame.index)
        scaled_data = self.scaler.fit_transform(training_data_frame['Close'].values.reshape(-1, 1))
        train_size = int(len(scaled_data) * 0.7)
        self.train_data, self.test_data = scaled_data[:train_size], scaled_data[train_size:]

    def generate_sequences(self, dataset, look_back=15):
        X, y = [], []
        for i in range(len(dataset) - look_back):
            X.append(dataset[i:i + look_back])
            y.append(dataset[i + look_back])
        return np.array(X), np.array(y)

    def load_pre_trained_model(self):
        try:
            self.model = load_model(self.pre_trained_model_path)
        except:
            self.model = None

    def fine_tune(self):
        if self.model is None:
            x_train, y_train = self.generate_sequences(self.train_data, self.look_back)
            x_test, y_test = self.generate_sequences(self.test_data, self.look_back)
            x_train = np.reshape(x_train, (x_train.shape[0], self.look_back, 1))
            x_test = np.reshape(x_test, (x_test.shape[0], self.look_back, 1))
            self.model = Sequential([
                LSTM(20, input_shape=(self.look_back, 1)),
                Dense(1)
            ])
            self.model.compile(optimizer=Adam(learning_rate=0.0001), loss='mean_squared_error', metrics=['mae'])
        else:
            if not hasattr(self, 'train_data') or self.train_data is None:
                raise ValueError("Training data is not available for fine-tuning.")

            x_train, y_train = self.generate_sequences(self.train_data, self.look_back)
            x_test, y_test = self.generate_sequences(self.test_data, self.look_back)
            x_train = np.reshape(x_train, (x_train.shape[0], self.look_back, 1))
            x_test = np.reshape(x_test, (x_test.shape[0], self.look_back, 1))
            
            self.model.compile(optimizer=Adam(learning_rate=0.0001), loss='mean_squared_error', metrics=['mae'])

        self.model.fit(x_train, y_train, epochs=5, batch_size=32, verbose=2)
        self.model.save(self.pre_trained_model_path)
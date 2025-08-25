"""
Redis Model Handler for Keras Models
Provides functionality to save and load Keras models to/from Redis.
Suppresses TensorFlow and future warnings for clean logs.
"""

import os
import sys
import warnings
import tempfile
from pathlib import Path

import redis
import tensorflow as tf
from keras.models import load_model, Model

# Environment Configuration
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'       # Suppress TensorFlow logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'     # Disable oneDNN optimizations
sys.stderr = open(os.devnull, 'w')            # Suppress stderr messages

tf.get_logger().setLevel('ERROR')
warnings.filterwarnings('ignore', category=FutureWarning)

# Redis Model Handler
class RedisModelHandler:
    """
    Handles storing and retrieving Keras models in Redis.
    Models are temporarily saved to disk before uploading or loading.
    """

    def __init__(self, host: str = "redis-service", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db)

    # Public Methods
    def set_model(self, model: Model, key: str = "keras_model") -> None:
        """
        Save a Keras model to Redis.

        Args:
            model (keras.Model): The Keras model to save.
            key (str): Redis key under which the model is stored.
        """
        fd, temp_path = tempfile.mkstemp(suffix=".h5")
        os.close(fd)
        try:
            model.save(temp_path)
            with open(temp_path, "rb") as f:
                self.redis.set(key, f.read())
        finally:
            os.remove(temp_path)

    def get_model(self, key: str = "keras_model") -> Model:
        """
        Load a Keras model from Redis.

        Args:
            key (str): Redis key where the model is stored.

        Returns:
            keras.Model: The loaded Keras model.

        Raises:
            ValueError: If the model does not exist in Redis.
        """
        data = self.redis.get(key)
        if not data:
            raise ValueError(f"No model found in Redis with key '{key}'")

        fd, temp_path = tempfile.mkstemp(suffix=".h5")
        os.close(fd)
        try:
            with open(temp_path, "wb") as f:
                f.write(data)
            return load_model(temp_path)
        finally:
            os.remove(temp_path)

if __name__ == "__main__":
    # Example: Load a local model and store it in Redis
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    model_file_path = PROJECT_ROOT / "assets" / "models" / "NPS_NABIL.h5"

    handler = RedisModelHandler()

    if model_file_path.exists():
        model = load_model(model_file_path)
        handler.set_model(model, "NPS_NABIL")
        print(f"Model '{model_file_path.name}' saved to Redis with key 'NPS_NABIL'.")
    else:
        print(f"Model file not found at {model_file_path}")
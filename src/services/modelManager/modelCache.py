import os
import sys
import warnings

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

sys.stderr = open(os.devnull, 'w')

import tensorflow as tf
from pathlib import Path
import tempfile
import redis
from keras.models import load_model

tf.get_logger().setLevel('ERROR')
warnings.filterwarnings('ignore', category=FutureWarning)

class RedisModelHandler:
    def __init__(self, host="redis-service", port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def set_model(self, model, key="keras_model"):
        fd, path = tempfile.mkstemp(suffix=".h5")
        os.close(fd)
        try:
            model.save(path)
            with open(path, "rb") as f:
                self.redis.set(key, f.read())
        finally:
            os.remove(path)

    def get_model(self, key="keras_model"):
        data = self.redis.get(key)
        if not data:
            raise ValueError(f"No model found in Redis with key '{key}'")
        fd, path = tempfile.mkstemp(suffix=".h5")
        os.close(fd)
        try:
            with open(path, "wb") as f:
                f.write(data)
            return load_model(path)
        finally:
            os.remove(path)

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    model_file_path = PROJECT_ROOT / "assets" / "models" / "NPS_NABIL.h5"

    handler = RedisModelHandler()

    model = load_model(model_file_path)
    handler.set_model(model, "NPS_NABIL")

    # model_from_redis = handler.get_model("LSTMModel")
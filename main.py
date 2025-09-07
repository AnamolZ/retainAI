import uvicorn
import os
import tensorflow as tf
import logging

logging.getLogger("absl").setLevel(logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

if __name__ == "__main__":
    uvicorn.run("src.services.predictAPI.predictAPI:app", host="0.0.0.0", port=8000, reload=True)
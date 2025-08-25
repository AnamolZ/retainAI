"""
Script sets up logging, suppresses unnecessary TensorFlow warnings,
and starts the Uvicorn server.
"""

import os
import logging
import uvicorn
import tensorflow as tf

# Suppress TensorFlow verbose logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')
logging.getLogger("absl").setLevel(logging.ERROR)

# Optional: Configure Python logging for this service
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

if __name__ == "__main__":
    logging.info("Service on 0.0.0.0:8000")
    uvicorn.run(
        "src.services.predictAPI.predictAPI:app",  # Path to FastAPI app
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable hot reload for development
    )
import uvicorn
import os
import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

if __name__ == "__main__":
    uvicorn.run("services.predictAPI.predictAPI:app", host="127.0.0.1", port=8000, reload=True)

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.usemodel.predictprice import ModelPredictor
from services.trainmodel.model import ModelFineTuning

app = FastAPI()

scheduler = BackgroundScheduler()

def train_model_periodically():
    fine_tuning_model = ModelFineTuning(
        training_data_path='/home/xznom/testing/dataPrice/dataPrice.csv',
        pre_trained_model_path='/home/xznom/testing/model/LSTMmodel.h5'
    )
    fine_tuning_model.data_frame_training()
    fine_tuning_model.load_pre_trained_model()
    fine_tuning_model.fine_tune()

scheduler.add_job(
    train_model_periodically, 
    CronTrigger(hour='10', minute='0', second='0', id='fine_tune_10am')
)
scheduler.add_job(
    train_model_periodically, 
    CronTrigger(hour='22', minute='0', second='0', id='fine_tune_10pm')
)

@app.on_event("startup")
def start_background_training():
    scheduler.start()

@app.get("/")
def modelApi():
    model_predictor = ModelPredictor(
        "/home/xznom/testing/dataPrice/dataPrice.csv",
        "/home/xznom/testing/model/LSTMmodel.h5"
    )
    prediction = model_predictor._generate_prediction()
    
    return {"prediction": float(prediction)}
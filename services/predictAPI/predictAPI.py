from config import RETAINAI_SCHEDULER_TIMES
from contextlib import asynccontextmanager
from fastapi import FastAPI

from apscheduler.schedulers.background import BackgroundScheduler
from services.usemodel.predictprice import ModelPredictor
from services.trainmodel.model import ModelFineTuning

# The @on_event decorator deprecated raixa so I removed it
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
scheduler = BackgroundScheduler()

# Localized paths
data_path = 'dataPrice/dataPrice.csv'
model_path = 'model/LSTMmodel.h5'


def train_model_periodically():
    fine_tuning_model = ModelFineTuning(
        training_data_path = data_path,
        pre_trained_model_path = model_path
    )
    fine_tuning_model.data_frame_training()
    fine_tuning_model.load_pre_trained_model()
    fine_tuning_model.fine_tune()

for time in RETAINAI_SCHEDULER_TIMES:
    scheduler.add_job(
        train_model_periodically, 
        "cron",
        **time
    )

@app.get("/")
def modelApi():
    model_predictor = ModelPredictor(data_path, model_path)
    prediction = model_predictor._generate_prediction()
    return {"prediction": float(prediction)}
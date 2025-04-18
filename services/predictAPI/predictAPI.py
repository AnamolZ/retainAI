import os
from config import RETAINAI_SCHEDULER_TIMES
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from apscheduler.schedulers.background import BackgroundScheduler
from services.usemodel.predictprice import ModelPredictor
from services.trainmodel.model import ModelFineTuning

from services.webscrapper.priceScrappy import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
scheduler = BackgroundScheduler()

fine_tuning_models = {}  # Dictionary to store multiple models by symbol

def set_paths(symbol):
    data_path = f"dataPrice/{symbol}Data.csv"
    model_path = f"model/{symbol}Model.h5"
    return data_path, model_path

def train_model_periodically(symbol: str):
    data_path, model_path = set_paths(symbol)
    fine_tuning_model = ModelFineTuning(
        training_data_path=data_path,
        pre_trained_model_path=model_path
    )
    fine_tuning_model.data_frame_training()
    fine_tuning_model.load_pre_trained_model()
    fine_tuning_model.fine_tune()
    fine_tuning_models[symbol] = fine_tuning_model

def add_scheduler_job(symbol): 
    for time in RETAINAI_SCHEDULER_TIMES:
        scheduler.add_job(
            train_model_periodically,
            "cron",
            **time,
            args=[symbol]
        )

@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join("ui", "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/train")
def train_model(symbol: str = Form(...)):
    train_model_periodically(symbol)
    return RedirectResponse(url="/", status_code=303)

@app.post("/schedule")
def train_model(symbol: str = Form(...)):
    add_scheduler_job(symbol)
    return RedirectResponse(url="/", status_code=303)

@app.get("/predict/{symbol}")
def predict(symbol: str):
    data_path, model_path = set_paths(symbol)
    model_predictor = ModelPredictor(data_path, model_path)
    prediction = model_predictor._generate_prediction()
    return {"symbol": symbol, "prediction": float(prediction)}

@app.post("/fetch_data")
def fetch_data(symbol: str = Form(...), stock_exchange: str = Form(...)):
    data_path, model_path = set_paths(symbol)
    scrapper = StockDataService(type = stock_exchange)
    data = scrapper.fetch_data(symbol)
    data.to_csv(data_path)



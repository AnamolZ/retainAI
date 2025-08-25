"""
FastAPI Application for RetainAI
Provides endpoints for stock price prediction via WhatsApp/Telegram,
background model training, caching, and scheduled scraping jobs.
"""

import os
import re
import asyncio
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Response, Request, BackgroundTasks
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from keras.models import load_model
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from twilio.rest import Client
from telegram import Update
from telegram.ext import ContextTypes

# RetainAI Modules
from ..usemodel.predictprice import ModelPredictor
from ..trainmodel.model import ModelFineTuning
from ..webscrapper.nps_priceScrappy import scrape_and_save
from ..webscrapper.nas_priceScrappy import StockDataService
from ..cacheManager.cacheManager import save_value, get_value
from ..modelManager.modelCache import RedisModelHandler
from ..database.postgresbase import PostgresDB

# Environment & Config
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
training_data_path = PROJECT_ROOT / "assets" / "dataPrice"
pre_trained_model_path = PROJECT_ROOT / "assets" / "models"

NAS_STOCKS = ["NVDA","MSFT","AAPL","AMZN","TSLA"]
NPS_STOCKS = ["NABIL","CIT","GBIME","EBL","HIDCL"]

# FastAPI App & Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Scheduler & Locks
scheduler = BackgroundScheduler()
train_lock = asyncio.Lock()
cache_predictions_lock = asyncio.Lock()
cache_model_lock = asyncio.Lock()
cache_priceData_lock = asyncio.Lock()
delete_files_lock = asyncio.Lock()

# Async Jobs
async def train_model_periodically():
    """Fine-tunes models for all NAS and NPS stocks."""
    async with train_lock:
        all_stocks = {"NAS": NAS_STOCKS, "NPS": NPS_STOCKS}
        for market, stocks in all_stocks.items():
            for symbol in stocks:
                try:
                    data_file = training_data_path / f"dataPrice{symbol}.csv"
                    model_file = pre_trained_model_path / f"{market}_{symbol}.h5"
                    if not data_file.exists():
                        print(f"WARNING: Missing data for {symbol}. Skipping.")
                        continue

                    ft_model = ModelFineTuning(data_file, model_file)
                    ft_model.data_frame_training()
                    ft_model.load_pre_trained_model()
                    ft_model.fine_tune()
                except Exception as e:
                    print(f"ERROR: Training {symbol} failed: {e}")

async def cache_predictions():
    """Caches predicted stock prices into Redis."""
    async with cache_predictions_lock:
        redis_handler = RedisModelHandler()
        all_stocks = {"NAS": NAS_STOCKS, "NPS": NPS_STOCKS}
        for market, stocks in all_stocks.items():
            for symbol in stocks:
                try:
                    data_file = training_data_path / f"dataPrice{symbol}.csv"
                    if not data_file.exists():
                        continue

                    model_key = f"{market}_{symbol}"
                    model = redis_handler.get_model(model_key)
                    predictor = ModelPredictor(data_file, model=model)
                    prediction = float(predictor._generate_prediction())
                    save_value(symbol, prediction)
                except Exception as e:
                    print(f"ERROR: Caching prediction for {symbol} failed: {e}")

async def cache_models():
    """Caches all pre-trained models into Redis."""
    async with cache_model_lock:
        redis_handler = RedisModelHandler()
        for model_file in pre_trained_model_path.glob("*.h5"):
            model = load_model(model_file)
            redis_handler.set_model(model, model_file.stem)

async def cache_price_data():
    """Saves CSV price data into PostgreSQL database."""
    async with cache_priceData_lock:
        postgres_handler = PostgresDB()
        for csv_file in training_data_path.glob("*.csv"):
            df = pd.read_csv(csv_file)
            await postgres_handler.save_data(df, csv_file.stem)

async def delete_files():
    """Deletes all CSV and H5 files after caching."""
    async with delete_files_lock:
        for file in training_data_path.glob("*.csv"):
            try: file.unlink(); print(f"Deleted {file}")
            except Exception as e: print(f"Failed to delete {file}: {e}")
        for file in pre_trained_model_path.glob("*.h5"):
            try: file.unlink(); print(f"Deleted {file}")
            except Exception as e: print(f"Failed to delete {file}: {e}")

def train_model_job():
    """Wrapper to run training, caching, and cleanup sequentially."""
    asyncio.run(train_model_periodically())
    asyncio.run(cache_models())
    asyncio.run(cache_predictions())
    asyncio.run(cache_price_data())
    asyncio.run(delete_files())

def scrape_all_stocks_job():
    """Scrapes stock data for all NAS and NPS symbols."""
    for symbol in NAS_STOCKS:
        try: StockDataService(symbol).save_to_csv()
        except Exception as e: print(f"Scraping NAS {symbol} failed: {e}")
    for symbol in NPS_STOCKS:
        try: scrape_and_save(symbol); print(f"Scraped NPS {symbol}")
        except Exception as e: print(f"Scraping NPS {symbol} failed: {e}")

# Scheduler Jobs
scheduler.add_job(
    train_model_job,
    CronTrigger(day_of_week='mon', hour=11, minute=0, second=0),
    # IntervalTrigger(minutes=7),
    id='monday_training',
    replace_existing=True
)

scheduler.add_job(
    scrape_all_stocks_job,
    CronTrigger(day_of_week='fri', hour=11, minute=0, second=0),
    # IntervalTrigger(minutes=5),
    id='friday_scraping',
    replace_existing=True
)

# Startup & Shutdown Events
@app.on_event("startup")
async def startup_event():
    print("Starting scheduler...")
    scheduler.start()
    print("Scheduler started.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Stopping scheduler...")
    scheduler.shutdown()
    print("Scheduler stopped.")

# Telegram / WhatsApp Prediction Handlers
async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /predict <MARKET_SYMBOL> <STOCK_SYMBOL>")
        return

    market, symbol = context.args[0].upper(), context.args[1].upper()
    if market not in ["NPS", "NAS"]:
        await update.message.reply_text("Invalid market. Use NPS or NAS.")
        return

    try:
        redis_handler = RedisModelHandler()
        model = redis_handler.get_model(f"{market}_{symbol}")
        data_file = training_data_path / f"dataPrice{symbol}.csv"
        predictor = ModelPredictor(data_file, model=model)
        prediction = float(predictor._generate_prediction())
        reply = f"Prediction for {symbol}: {prediction:.2f}"
    except ValueError as e:
        reply = f"No cached model for {symbol}. {e}"
    except FileNotFoundError:
        reply = f"No training data for {symbol} yet."
    except Exception as e:
        reply = f"Error predicting {symbol}: {e}"

    await update.message.reply_text(reply)

@app.post("/whatsapp")
async def whatsapp_repo(background_tasks: BackgroundTasks,
                        body: str = Form(..., alias="Body"),
                        from_number: str = Form(..., alias="From"),
                        to_number: str = Form(..., alias="To")):
    body = body.strip()
    match = re.match(r"(?i)^(NPS|NAS)\s+([A-Za-z0-9]+)$", body)

    if not match:
        reply = "Invalid Parameter. Format: NPS or NAS <stock_symbol>"
        xml = f"<Response><Message><Body>{escape(reply)}</Body></Message></Response>"
        return Response(content=xml, media_type="application/xml")

    market, symbol = match.group(1).upper(), match.group(2).upper()

    def task():
        try:
            prediction = get_value(symbol)
            if prediction is None:
                redis_handler = RedisModelHandler()
                model = redis_handler.get_model(f"{market}_{symbol}")
                data_file = training_data_path / f"dataPrice{symbol}.csv"
                predictor = ModelPredictor(data_file, model=model)
                prediction = float(predictor._generate_prediction())
                save_value(symbol, prediction)
            result = f"Prediction for {symbol}: {prediction:.2f}"
        except (ValueError, FileNotFoundError) as e:
            result = f"Error: {e}"
        except Exception as e:
            result = f"Error processing {symbol}: {e}"

        client.messages.create(from_=to_number, to=from_number, body=result)

    background_tasks.add_task(task)
    ack = f"Request received for {symbol} ({market}). You will receive the prediction shortly."
    xml = f"<Response><Message><Body>{escape(ack)}</Body></Message></Response>"
    return Response(content=xml, media_type="application/xml")

# Health Check / API
@app.get("/")
@limiter.limit("5/minute")
def model_api(request: Request):
    return {"message": "Hello! RetainAI is running..."}
import re
import asyncio
from pathlib import Path
from xml.sax.saxutils import escape

import os
import pandas as pd
from dotenv import load_dotenv

from fastapi import FastAPI, Form, Response, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from twilio.rest import Client
from telegram import Update
from telegram.ext import ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from ..usemodel.predictprice import ModelPredictor
from ..trainmodel.model import ModelFineTuning
from ..webscrapper.nps_priceScrappy import scrape_and_save
from ..webscrapper.nas_priceScrappy import StockDataService
from ..cacheManager.cacheManager import save_value, get_value
from ..modelManager.modelCache import RedisModelHandler
from ..database.postgresbase import PostgresDB

from keras.models import load_model

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

origins = [
    "http://localhost:5173",
    "http://localhost:30573",
]

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

training_data_path = PROJECT_ROOT / "assets" / "dataPrice"
pre_trained_model_path = PROJECT_ROOT / "assets" / "models"

scheduler = BackgroundScheduler()
train_lock = asyncio.Lock()
cache_predictions_lock = asyncio.Lock()
cache_model_lock = asyncio.Lock()
cache_priceData_lock = asyncio.Lock()
delete_files_lock = asyncio.Lock()

NAS = ["NVDA","MSFT","AAPL","AMZN","TSLA"]
NPS = ["GBIME","NABIL","CIT","EBL","HIDCL"]

async def train_model_periodically():
    """
    Asynchronously fine-tunes a separate prediction model for each stock.
    It iterates through NAS and NPS lists, training each model with its
    corresponding data file. A lock prevents concurrent training runs.
    """
    async with train_lock:
        
        # Combine all stocks into a dictionary to associate them with their market
        all_stocks = {"NAS": NAS, "NPS": NPS}

        for market, stock_list in all_stocks.items():
            for stock_symbol in stock_list:
                try:
                    stock_data_path = training_data_path / f"dataPrice{stock_symbol}.csv"
                    stock_model_path = pre_trained_model_path / f"{market}_{stock_symbol}.h5"

                    # Check if the data file exists before proceeding
                    if not stock_data_path.exists():
                        print(f"WARNING: Data file not found for {stock_symbol} at {stock_data_path}. Skipping training.")
                        continue

                    # Instantiate the fine-tuning class with specific paths for stock
                    fine_tuning_model = ModelFineTuning(stock_data_path, stock_model_path)
                    fine_tuning_model.data_frame_training()
                    fine_tuning_model.load_pre_trained_model()
                    fine_tuning_model.fine_tune()

                except Exception as e:
                    print(f"ERROR: An error occurred while training model for {stock_symbol}: {e}")

async def cache_predictions():
    """
    Asynchronously caches the predicted stock prices in Redis.
    It retrieves the predictions for each stock and saves them with a TTL.
    """
    async with cache_predictions_lock:
        redis_handler = RedisModelHandler()	
        all_stocks = {"NAS": NAS, "NPS": NPS}

        for market, stock_list in all_stocks.items():
            for stock_symbol in stock_list:
                try:
                    stock_data_path = training_data_path / f"dataPrice{stock_symbol}.csv"
                    # stock_model_path = pre_trained_model_path / f"{market}_{stock_symbol}.h5"

                    if not stock_data_path.exists():
                        print(f"WARNING: Data file not found for {stock_symbol} at {stock_data_path}. Skipping caching.")
                        continue

                    # Fetch model from Redis
                    model_key = f"{market}_{stock_symbol}"	
                    model = redis_handler.get_model(model_key)	

                    # Get prediction using the cached model	
                    model_predictor = ModelPredictor(stock_data_path, model=model)	
                    prediction = float(model_predictor._generate_prediction())

                    save_value(stock_symbol, prediction)

                except Exception as e:
                    print(f"ERROR: An error occurred while caching prediction for {stock_symbol}: {e}")

async def cacheModel():
    """
    Asynchronously caches all pre-trained models in Redis.
    It loads each model from the specified directory and saves it with its filename as the key.
    """
    async with cache_model_lock:
        PROJECT_ROOT = Path(__file__).resolve().parents[3]
        model_file_path = PROJECT_ROOT / "assets" / "models"

        redis_handler = RedisModelHandler()

        for model_file in model_file_path.glob("*.h5"):
            model = load_model(model_file)
            redis_handler.set_model(model, model_file.stem)

async def cachePriceData():
    """
    Asynchronously caches all price data CSV files into the PostgreSQL database.
    It reads each CSV file in the specified directory and saves it to the database.
    """
    async with cache_priceData_lock:
        PROJECT_ROOT = Path(__file__).resolve().parents[3]
        priceData_file_path = PROJECT_ROOT / "assets" / "dataPrice"

        postgres_handler = PostgresDB()

        for priceData_file in priceData_file_path.glob("*.csv"):
            dataframe = pd.read_csv(priceData_file)
            table_name = priceData_file.stem
            
            await asyncio.to_thread(postgres_handler.save_data, dataframe, table_name)

async def delete_files():
    """
    Deletes all files from both dataPrice (CSV) and models (H5).
    """
    async with delete_files_lock:
        data_path = PROJECT_ROOT / "assets" / "dataPrice"
        model_path = PROJECT_ROOT / "assets" / "models"

        for file in data_path.glob("*.csv"):
            try:
                file.unlink()
                print(f"Deleted data file: {file}")
            except Exception as e:
                print(f"ERROR: Could not delete data file {file}: {e}")

        for file in model_path.glob("*.h5"):
            try:
                file.unlink()
                print(f"Deleted model file: {file}")
            except Exception as e:
                print(f"ERROR: Could not delete model file {file}: {e}")

def train_model_job():
    """Wrapper to run training first, then caching predictions."""
    async def run_all():
        await train_model_periodically()
        await cacheModel()
        await cache_predictions()
        await cachePriceData()
        await delete_files()

    asyncio.run(run_all())

def scrape_all_stocks_job():
    """
    Scrapes data for all stocks in NAS and NPS lists and saves it to CSV files.
    This job is designed to replace old files with new data on each run.
    """
    for stock_symbol in NAS:
        try:
            stock_service = StockDataService(stock_symbol)
            stock_service.save_to_csv()
        except Exception as e:
            print(f"Error scraping data for NAS stock {stock_symbol}: {e}")

    for stock_symbol in NPS:
        try:
            scrape_and_save(stock_symbol)
            print(f"Successfully scraped and saved data for {stock_symbol}")
        except Exception as e:
            print(f"Error scraping data for NPS stock {stock_symbol}: {e}")

scheduler.add_job(
    train_model_job,
    # CronTrigger(day_of_week='mon', hour=11, minute=0, second=0),
    IntervalTrigger(minutes=2),
    id='monday_training',
    replace_existing=True
)

scheduler.add_job(
    scrape_all_stocks_job,
    # CronTrigger(day_of_week='fri', hour=11, minute=0, second=0),
    IntervalTrigger(minutes=1),
    id='friday_scraping',
    replace_existing=True
)

@app.on_event("startup")
async def startup_event():
    """
    Starts the scheduler on application startup.
    The scheduler will immediately run any pending jobs (like the scraping job)
    and then continue based on their defined triggers.
    """
    print("Application startup: Starting scheduler...")
    scheduler.start()
    print("Scheduler started.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shuts down the scheduler gracefully on application shutdown.
    """
    print("Application shutdown: Stopping scheduler...")
    scheduler.shutdown()
    print("Scheduler stopped.")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /predict <MARKET_SYMBOL> <STOCK_SYMBOL>")
        return
    
    market_symbol = context.args[0].upper()
    stock_symbol = context.args[1].upper()

    if market_symbol not in ["NPS", "NAS"]:
        await update.message.reply_text("Invalid market. Please use NPS or NAS.")
        return

    try:
        redis_handler = RedisModelHandler()
        
        model_key = f"{market_symbol}_{stock_symbol}"
        model = redis_handler.get_model(model_key)
        
        stock_data_path = training_data_path / f"dataPrice{stock_symbol}.csv"
        model_predictor = ModelPredictor(data_path=stock_data_path, model=model)
        
        prediction = model_predictor._generate_prediction()
        reply = f"Prediction for {stock_symbol}: {float(prediction):.2f}"

    except ValueError as e:
        reply = f"Could not find a cached model for {stock_symbol}. Please wait for the next training cycle. Details: {e}"
    except FileNotFoundError:
        reply = f"Training data for {stock_symbol} not found. Please wait for the next scraping cycle."
    except Exception as e:
        reply = f"An error occurred while predicting for {stock_symbol}: {e}"

    await update.message.reply_text(reply)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
@limiter.limit("5/minute")
def modelApi(request: Request):
    # client.messages.create(
    #     from_='whatsapp:+14155238886',
    #     body="Hello! A static message from RetainAI 🚀",
    #     to='whatsapp:+9779862328620'
    # )

    return {"Hello! A static message from RetainAI 🚀"}

@app.post("/whatsapp")
async def whatsapp_repo(background_tasks: BackgroundTasks,
                        body: str = Form(..., alias="Body"),
                        from_number: str = Form(..., alias="From"),
                        to_number: str = Form(..., alias="To")):
    body = body.strip()
    match = re.match(r"(?i)^(NPS|NAS)\s+([A-Za-z0-9]+)$", body)

    if not match:
        reply = "Invalid Parameter. Please use the format: NPS or NAS <stock_symbol>"
        xml = f"<Response><Message><Body>{escape(reply)}</Body></Message></Response>"
        return Response(content=xml, media_type="application/xml")

    market_symbol, stock_symbol = match.group(1).upper(), match.group(2).upper()

    def task():
        try:
            prediction = get_value(stock_symbol)
            
            if prediction is not None:
                prediction = float(prediction)
            else:
                redis_handler = RedisModelHandler()

                model_key = f"{market_symbol}_{stock_symbol}"
                model = redis_handler.get_model(model_key)
                
                stock_data_path = training_data_path / f"dataPrice{stock_symbol}.csv"
                
                model_predictor = ModelPredictor(data_path=stock_data_path, model=model)
                prediction = float(model_predictor._generate_prediction())
                
                save_value(stock_symbol, prediction)

            result = f"Prediction for {stock_symbol}: {prediction:.2f}"
            
        except ValueError:
             result = f"Error: Model for {stock_symbol} not found in cache. Please try again later."
        except FileNotFoundError:
            result = f"Error: Training data for {stock_symbol} not found."
        except Exception as e:
            result = f"Error processing {stock_symbol}: {str(e)}"

        client.messages.create(
            from_=to_number,
            to=from_number,
            body=result
        )

    background_tasks.add_task(task)

    ack = f"Request received for {stock_symbol} ({market_symbol}). You will receive the prediction shortly."
    xml = f"<Response><Message><Body>{escape(ack)}</Body></Message></Response>"
    return Response(content=xml, media_type="application/xml")


@app.get("/stocks/{symbol}")
async def get_stock_data(symbol: str):
    """
    Fetches the last 30 days of stock data from the PostgreSQL database
    and the latest prediction from Redis.
    """
    try:
        postgres_handler = PostgresDB()
        table_name = f"dataPrice{symbol.upper()}"

        # This is the corrected line
        query = f'SELECT * FROM "{table_name}" ORDER BY "Date" DESC LIMIT 30'
        df = postgres_handler.fetch_data(query)

        # Also, make sure to sort the data for the chart
        if not df.empty:
            df = df.sort_values(by="Date", ascending=True).reset_index(drop=True)

        if df.empty:
            return JSONResponse(
                content={"error": f"No historical data found for {symbol} in the database."},
                status_code=404
            )

        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                "timestamp": row["Date"],
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
            })

        prediction = get_value(symbol)
        
        return {"symbol": symbol, "chartData": chart_data, "prediction": prediction}

    except Exception as e:
        print(f"ERROR: Could not fetch data for {symbol}. Reason: {e}")
        return JSONResponse(content={"error": "An internal server error occurred."}, status_code=500)
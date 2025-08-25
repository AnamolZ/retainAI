"""
Redis caching utility for predicted stock prices.
Provides functions to save and retrieve predictions with optional TTL.
"""

import redis
import json
import logging
from typing import Optional

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Redis Client Initialization
redis_client = redis.Redis(host="redis-service", port=6379, db=0)

# Redis Cache Functions
def save_value(symbol: str, price: float, ttl: int = 43200) -> None:
    """
    Save predicted stock price in Redis with expiration time.
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL').
        price (float): Predicted stock price.
        ttl (int, optional): Time-to-live in seconds. Default is 12 hours (43200s).
    """
    key = f"prediction_value:{symbol.upper()}"
    redis_client.set(key, json.dumps(price), ex=ttl)
    logging.info(f"Redis cache updated for {symbol.upper()} (expires in {ttl} seconds).")


def get_value(symbol: str) -> Optional[float]:
    """
    Retrieve predicted stock price from Redis.
    
    Args:
        symbol (str): Stock symbol to fetch.
    
    Returns:
        Optional[float]: Cached price if exists, otherwise None.
    """
    key = f"prediction_value:{symbol.upper()}"
    value = redis_client.get(key)
    if value is None:
        logging.info(f"No cached value found for {symbol.upper()}.")
        return None
    return float(json.loads(value))


if __name__ == "__main__":
    # Save a sample value with 5-minute TTL
    save_value("AAPL", 214.95, ttl=300)
    
    # Retrieve the saved value
    price = get_value("AAPL")
    logging.info(f"Retrieved predicted price for AAPL: {price}")
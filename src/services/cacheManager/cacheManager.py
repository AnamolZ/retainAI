
import redis
import json
from typing import Optional

r = redis.Redis(host="redis-service", port=6379, db=0)

def save_value(symbol: str, price: float, ttl: int = 43200):
    """
    Save predicted stock price in Redis with expiration time.
    Default TTL = 12 hours (43200 seconds).
    """
    key = f"prediction_value:{symbol.upper()}"
    r.set(key, json.dumps(price), ex=ttl)
    print(f"CacheUpdated Updated for {symbol} in Redis (expires in {ttl} seconds).")


def get_value(symbol: str) -> Optional[float]:
    """
    Retrieve predicted stock price from Redis.
    Returns None if not found.
    """
    key = f"prediction_value:{symbol.upper()}"
    value = r.get(key)
    if value is None:
        return None
    return float(json.loads(value))

if __name__ == "__main__":
    save_value("AAPL", 214.95, ttl=300) # right now: 5 minutes
    price = get_value("AAPL")
    print(f"Retrieved predicted price for AAPL: {price}")
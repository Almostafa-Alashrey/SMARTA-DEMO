import os
import time
import random
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/api/v1/telemetry")

def generate_telemetry(tick: int) -> dict:
    temperature = round(random.uniform(18.0, 24.0), 2)
    humidity = round(random.uniform(45.0, 60.0), 2)

    if tick % 10 == 0:
        temperature = round(random.uniform(38.0, 48.0), 2)
        logging.warning(f"⚠️ [ANOMALY INJECTED] Temperature spike triggered: {temperature}°C")

    return {
        "sensor_id": "SMARTA-WH-01",
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": temperature,
        "humidity": humidity
    }

def main():
    logging.info("🚀 Starting SMARTA IoT Simulator Service...")
    tick = 1
    while True:
        payload = generate_telemetry(tick)
        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=2)
            logging.info(f"Tick #{tick} | Sent: {payload['temperature']}°C | Response: {response.status_code}")
        except requests.exceptions.RequestException:
            logging.info(f"Tick #{tick} | Waiting for Backend...")
        tick += 1
        time.sleep(3)

if __name__ == "__main__":
    main()
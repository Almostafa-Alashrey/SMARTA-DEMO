import os
import time
import random
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/api/v1/telemetry")

# الأماكن المتاحة في المخزن
LOCATIONS = ["Shelf A1", "Shelf B2", "Shelf C3"]

def generate_telemetry(tick: int) -> dict:
    loc = random.choice(LOCATIONS)
    sensor_id = f"SENS-{loc.replace(' ', '')}"
    
    # قراءات طبيعية
    temperature = round(random.uniform(18.0, 24.0), 2)
    humidity = round(random.uniform(45.0, 60.0), 2)
    gas_level = round(random.uniform(0.1, 0.5), 2) # مستوى الإيثيلين الطبيعي

    # حقن الـ Anomaly كل 10 ثواني في رف معين
    if tick % 10 == 0:
        temperature = round(random.uniform(35.0, 45.0), 2)
        gas_level = round(random.uniform(2.5, 5.0), 2) # الغاز بيزيد لما الحاجة تبوظ
        logging.warning(f"⚠️ [ANOMALY INJECTED] Spoilage simulated at {loc} (Gas: {gas_level}ppm)!")

    return {
        "sensor_id": sensor_id,
        "location": loc,
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": temperature,
        "humidity": humidity,
        "gas_level": gas_level
    }

def main():
    logging.info("🚀 Starting SMARTA Advanced IoT Simulator...")
    tick = 1
    while True:
        payload = generate_telemetry(tick)
        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=2)
            logging.info(f"Tick #{tick} | {payload['location']} | Sent Gas: {payload['gas_level']}ppm | Resp: {response.status_code}")
        except requests.exceptions.RequestException:
            logging.info(f"Tick #{tick} | Waiting for Backend...")
        tick += 1
        time.sleep(3)

if __name__ == "__main__":
    main()
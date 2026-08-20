# import os
# import time
# import random
# import logging
# import requests
# from datetime import datetime

# logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1/telemetry")
# # الأماكن المتاحة في المخزن
# LOCATIONS = ["Shelf A1", "Shelf B2", "Shelf C3"]

# def generate_telemetry(tick: int) -> dict:
#     loc = random.choice(LOCATIONS)
#     sensor_id = f"SENS-{loc.replace(' ', '')}"
    
#     # قراءات طبيعية
#     temperature = round(random.uniform(18.0, 24.0), 2)
#     humidity = round(random.uniform(45.0, 60.0), 2)
#     gas_level = round(random.uniform(0.1, 0.5), 2) # مستوى الإيثيلين الطبيعي

#     # حقن الـ Anomaly كل 10 ثواني في رف معين
#     if tick % 10 == 0:
#         temperature = round(random.uniform(35.0, 45.0), 2)
#         gas_level = round(random.uniform(2.5, 5.0), 2) # الغاز بيزيد لما الحاجة تبوظ
#         logging.warning(f"⚠️ [ANOMALY INJECTED] Spoilage simulated at {loc} (Gas: {gas_level}ppm)!")

#     return {
#         "sensor_id": sensor_id,
#         "location": loc,
#         "timestamp": datetime.utcnow().isoformat(),
#         "temperature": temperature,
#         "humidity": humidity,
#         "gas_level": gas_level
#     }

# def main():
#     logging.info("🚀 Starting SMARTA Advanced IoT Simulator...")
#     tick = 1
#     while True:
#         payload = generate_telemetry(tick)
#         try:
#             response = requests.post(BACKEND_URL, json=payload, timeout=2)
#             logging.info(f"Tick #{tick} | {payload['location']} | Sent Gas: {payload['gas_level']}ppm | Resp: {response.status_code}")
#         except requests.exceptions.RequestException:
#             logging.info(f"Tick #{tick} | Waiting for Backend...")
#         tick += 1
#         time.sleep(3)

# if __name__ == "__main__":
#     main()


# import time
# import random
# import requests
# from datetime import datetime

# API_URL = "http://localhost:8000/api/v1/telemetry"
# SHELVES = ["Shelf A1", "Shelf B1", "Shelf B2", "Bay C3"]

# def generate_telemetry(shelf_id: str) -> dict:
#     is_spike = random.random() < 0.05
    
#     if is_spike:
#         temp = round(random.uniform(32.0, 42.0), 2)
#         hum = round(random.uniform(76.0, 88.0), 2)
#         gas = round(random.uniform(2.5, 6.0), 2)
#     else:
#         temp = round(random.uniform(2.0, 12.0), 2)
#         hum = round(random.uniform(60.0, 80.0), 2)
#         gas = round(random.uniform(0.1, 0.8), 2)

#     return {
#         "sensor_id": f"sensor_{shelf_id.lower().replace(' ', '_')}",
#         "location": shelf_id,
#         "timestamp": datetime.now().isoformat(),
#         "temperature": temp,
#         "humidity": hum,
#         "gas_level": gas
#     }

# def start_simulation(interval_seconds: int = 3):
#     print(f"🚀 Starting SMARTA IoT Telemetry Simulator...")
#     print(f"📡 Target Endpoint: {API_URL}")
#     print(f"⏱️ Transmission Interval: Every {interval_seconds} seconds. Press Ctrl+C to stop.\n")

#     while True:
#         for shelf in SHELVES:
#             payload = generate_telemetry(shelf)
#             try:
#                 response = requests.post(API_URL, json=payload, timeout=3)
#                 if response.status_code == 200:
#                     res_data = response.json()
#                     status_flag = "⚠️ ANOMALY DETECTED" if res_data.get("is_anomaly") == 1 else "✅ NORMAL"
#                     print(f"[{payload['timestamp']}] {shelf} | Temp: {payload['temperature']}°C | Hum: {payload['humidity']}% | Gas: {payload['gas_level']} ppm | {status_flag}")
#                 else:
#                     print(f"❌ Failed to push data: Server returned {response.status_code}")
#             except requests.exceptions.ConnectionError:
#                 print(f"⚠️ Connection Refused: Ensure FastAPI backend is running locally at http://localhost:8000")
#             except Exception as e:
#                 print(f"❌ Transmission Error: {e}")

#             time.sleep(interval_seconds)

# if __name__ == "__main__":
#     start_simulation(interval_seconds=3)


import os
import time
import random
import logging
import requests
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Target backend telemetry endpoint
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1/telemetry")

LOCATIONS = ["Shelf A1", "Shelf B2", "Shelf C3"]

def generate_telemetry(tick: int) -> dict:
    loc = random.choice(LOCATIONS)
    sensor_id = f"SENS-{loc.replace(' ', '')}"
    
    # Normal operational parameters
    temperature = round(random.uniform(18.0, 24.0), 2)
    humidity = round(random.uniform(45.0, 60.0), 2)
    gas_level = round(random.uniform(0.1, 0.5), 2)

    # Anomaly injection every 10 ticks
    if tick % 10 == 0:
        temperature = round(random.uniform(35.0, 45.0), 2)
        humidity = round(random.uniform(76.0, 85.0), 2)
        gas_level = round(random.uniform(2.5, 5.0), 2)
        logging.warning(f"⚠️ [ANOMALY INJECTED] Spoilage simulated at {loc} (Gas: {gas_level}ppm, Temp: {temperature}°C)!")

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
            if response.status_code == 200:
                res_data = response.json()
                flag = "⚠️ ANOMALY" if res_data.get("is_anomaly") == 1 else "✅ NORMAL"
                logging.info(f"Tick #{tick} | {payload['location']} | Gas: {payload['gas_level']}ppm | Temp: {payload['temperature']}°C | Status: {flag}")
            else:
                logging.error(f"Tick #{tick} | Server HTTP {response.status_code}")
        except requests.exceptions.RequestException:
            logging.info(f"Tick #{tick} | Waiting for Backend at {BACKEND_URL}...")
        
        tick += 1
        time.sleep(3)

if __name__ == "__main__":
    main()
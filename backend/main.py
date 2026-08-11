import os
import sqlite3
import logging
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
app = FastAPI(title="SMARTA AI Backend")

DB_PATH = os.getenv("SQLITE_DB_PATH", "/app/data/smarta.db")

# البافر دلوقتي هيشيل 3 قراءات لكل سطر
telemetry_buffer = []
model = IsolationForest(contamination=0.1, random_state=42)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT,
            location TEXT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            gas_level REAL,
            is_anomaly INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class TelemetryPayload(BaseModel):
    sensor_id: str
    location: str
    timestamp: str
    temperature: float
    humidity: float
    gas_level: float

@app.post("/api/v1/telemetry")
def receive_telemetry(payload: TelemetryPayload):
    global telemetry_buffer
    is_anomaly = 0
    
    # تجهيز الداتا للـ ML
    features = [payload.temperature, payload.humidity, payload.gas_level]
    telemetry_buffer.append(features)
    
    if len(telemetry_buffer) > 10:
        if len(telemetry_buffer) > 50:
            telemetry_buffer.pop(0)
        
        # تدريب الموديل على الـ 3 عوامل
        model.fit(telemetry_buffer)
        prediction = model.predict([features])
        
        if prediction[0] == -1:
            is_anomaly = 1
            logging.warning(f"🚨 AI ANOMALY DETECTED AT {payload.location}! Gas: {payload.gas_level}ppm")

    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO telemetry (sensor_id, location, timestamp, temperature, humidity, gas_level, is_anomaly) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (payload.sensor_id, payload.location, payload.timestamp, payload.temperature, payload.humidity, payload.gas_level, is_anomaly)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database write failed")

    return {"status": "success", "anomaly_detected": bool(is_anomaly)}
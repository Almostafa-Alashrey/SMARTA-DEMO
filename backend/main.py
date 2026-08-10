import sqlite3
import logging
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
app = FastAPI(title="SMARTA AI Backend")

temperature_buffer = []
model = IsolationForest(contamination=0.1, random_state=42)

def init_db():
    conn = sqlite3.connect("smarta.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            is_anomaly INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class TelemetryPayload(BaseModel):
    sensor_id: str
    timestamp: str
    temperature: float
    humidity: float

@app.post("/api/v1/telemetry")
def receive_telemetry(payload: TelemetryPayload):
    global temperature_buffer
    is_anomaly = 0
    temperature_buffer.append([payload.temperature])
    
    if len(temperature_buffer) > 10:
        if len(temperature_buffer) > 50:
            temperature_buffer.pop(0)
        model.fit(temperature_buffer)
        prediction = model.predict([[payload.temperature]])
        if prediction[0] == -1:
            is_anomaly = 1
            logging.warning(f"🚨 AI DETECTED ANOMALY! Temp: {payload.temperature}°C")

    try:
        conn = sqlite3.connect("smarta.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO telemetry (sensor_id, timestamp, temperature, humidity, is_anomaly) VALUES (?, ?, ?, ?, ?)",
            (payload.sensor_id, payload.timestamp, payload.temperature, payload.humidity, is_anomaly)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database write failed")

    return {"status": "success", "anomaly_detected": bool(is_anomaly)}
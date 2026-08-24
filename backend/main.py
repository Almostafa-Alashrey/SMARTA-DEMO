import os
import math
import warnings
import base64
import cv2
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, Form
from sklearn.ensemble import IsolationForest
from vision import analyze_image

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

app = FastAPI(title="SMARTA Real-Time API")

SMARTA_CACHE = {
    "baselines": None,
    "inventory": None,
    "telemetry_buffer": []
}

model = IsolationForest(contamination=0.05, random_state=42, n_jobs=1)

def get_db_connection():
    pooler_url = "postgresql://postgres.fhfxqryxspsaohzojjmz:dDwK7YuKfIJ893JS@aws-1-eu-west-1.pooler.supabase.com:5432/postgres"
    return psycopg2.connect(pooler_url)

def init_postgres_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id SERIAL PRIMARY KEY,
            sensor_id VARCHAR(50),
            location VARCHAR(50),
            timestamp TIMESTAMP,
            temperature REAL,
            humidity REAL,
            gas_level REAL,
            is_anomaly INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            item_name VARCHAR(100),
            shelf_id VARCHAR(50),
            confidence REAL,
            days_remaining INTEGER,
            exp_date DATE,
            risk_level VARCHAR(20)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produce_baselines (
            item_name VARCHAR(50) PRIMARY KEY,
            optimal_temp_c REAL,
            max_days INTEGER
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM produce_baselines")
    if cursor.fetchone()[0] == 0:
        default_produce = [
            ('apple', 0.0, 90), ('banana', 13.0, 7), 
            ('orange', 4.0, 30), ('carrot', 0.0, 28), ('broccoli', 0.0, 14)
        ]
        cursor.executemany(
            "INSERT INTO produce_baselines (item_name, optimal_temp_c, max_days) VALUES (%s, %s, %s)",
            default_produce
        )

    conn.commit()
    cursor.close()
    conn.close()

def load_baselines_to_cache():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM produce_baselines")
    rows = cursor.fetchall()
    SMARTA_CACHE["baselines"] = {row['item_name']: (row['optimal_temp_c'], row['max_days']) for row in rows}
    cursor.close()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_postgres_db()
    load_baselines_to_cache()

@app.post("/api/v1/telemetry")
def receive_telemetry(data: dict):
    try:
        temp, hum, gas = float(data.get('temperature', 0.0)), float(data.get('humidity', 0.0)), float(data.get('gas_level', 0.0))
        sensor_id, location, timestamp = str(data.get('sensor_id', 'SENS-01')), str(data.get('location', 'Shelf A1')), str(data.get('timestamp', datetime.now().isoformat()))

        is_anomaly = 0
        buffer = SMARTA_CACHE["telemetry_buffer"]

        if len(buffer) >= 10:
            model.fit(np.array(buffer))
            pred = model.predict([[temp, hum, gas]])[0]
            if pred == -1 and (temp > 30.0 or hum > 75.0 or gas > 2.0):
                is_anomaly = 1

        if is_anomaly == 0:
            buffer.append([temp, hum, gas])
            if len(buffer) > 100: buffer.pop(0)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO telemetry (sensor_id, location, timestamp, temperature, humidity, gas_level, is_anomaly)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (sensor_id, location, timestamp, temp, hum, gas, is_anomaly))
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "ok", "is_anomaly": is_anomaly}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/v1/scan-veggie")
async def scan_veggie(file: UploadFile = File(...), shelf_id: str = Form("Shelf A1")):
    image_bytes = await file.read()
    detection = analyze_image(image_bytes)

    if not detection.get("detected"):
        return {"success": False, "message": "No recognizable produce detected."}

    item_key = detection["primary_item"].lower()
    
    baselines = SMARTA_CACHE["baselines"]
    if item_key not in baselines:
        opt_temp, base_days = (4.0, 10)
    else:
        opt_temp, base_days = baselines[item_key]

    current_temp, current_hum = 20.0, 60.0 
    
    temp_diff = max(0.0, current_temp - opt_temp)
    degradation_factor = math.pow(2.0, temp_diff / 10.0)
    hum_factor = 1.25 if current_hum < 85.0 else 1.0
    adjusted_days = max(1, round(base_days / (degradation_factor * hum_factor)))
    exp_date = (datetime.now() + timedelta(days=adjusted_days)).strftime("%Y-%m-%d")
    risk_level = "High" if adjusted_days <= 3 else "Moderate" if adjusted_days <= 7 else "Low"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO inventory (item_name, shelf_id, confidence, days_remaining, exp_date, risk_level)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (detection["primary_item"], shelf_id, detection["confidence"], adjusted_days, exp_date, risk_level))
    db_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    SMARTA_CACHE["inventory"] = None

    # تجهيز الصورة بالـ Bounding Box وإرسالها كـ Base64
    annotated_base64 = None
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if "annotated_frame" in detection:
            _, encoded_img = cv2.imencode('.jpg', detection["annotated_frame"])
            annotated_base64 = base64.b64encode(encoded_img).decode('utf-8')
    except Exception:
        pass

    return {
        "success": True, 
        "inventory_id": db_id,
        "annotated_image_base64": annotated_base64,
        "freshness_assessment": {
            "item": detection["primary_item"].capitalize(), 
            "estimated_days_remaining": adjusted_days,
            "estimated_expiration_date": exp_date, 
            "degradation_risk": risk_level, 
            "optimal_temp_c": opt_temp
        }
    }

@app.get("/api/v1/inventory")
def fetch_inventory():
    if SMARTA_CACHE["inventory"] is not None:
        return {"success": True, "inventory": SMARTA_CACHE["inventory"], "source": "cache"}

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM inventory ORDER BY id DESC")
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    SMARTA_CACHE["inventory"] = items
    return {"success": True, "inventory": items, "source": "database"}

@app.get("/api/v1/telemetry")
def fetch_telemetry():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT 300")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"success": True, "telemetry": rows}
    except Exception as e:
        return {"success": False, "message": str(e)}
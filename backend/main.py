# import os
# import sqlite3
# import logging
# import numpy as np
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from sklearn.ensemble import IsolationForest

# logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
# app = FastAPI(title="SMARTA AI Backend")

# DB_PATH = os.getenv("SQLITE_DB_PATH", "/app/data/smarta.db")

# # البافر دلوقتي هيشيل 3 قراءات لكل سطر
# telemetry_buffer = []
# model = IsolationForest(contamination=0.1, random_state=42)

# def init_db():
#     os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
#     conn = sqlite3.connect(DB_PATH, timeout=10)
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS telemetry (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             sensor_id TEXT,
#             location TEXT,
#             timestamp TEXT,
#             temperature REAL,
#             humidity REAL,
#             gas_level REAL,
#             is_anomaly INTEGER
#         )
#     ''')
#     conn.commit()
#     conn.close()

# init_db()

# class TelemetryPayload(BaseModel):
#     sensor_id: str
#     location: str
#     timestamp: str
#     temperature: float
#     humidity: float
#     gas_level: float

# @app.post("/api/v1/telemetry")
# def receive_telemetry(payload: TelemetryPayload):
#     global telemetry_buffer
#     is_anomaly = 0
    
#     # تجهيز الداتا للـ ML
#     features = [payload.temperature, payload.humidity, payload.gas_level]
#     telemetry_buffer.append(features)
    
#     if len(telemetry_buffer) > 10:
#         if len(telemetry_buffer) > 50:
#             telemetry_buffer.pop(0)
        
#         # تدريب الموديل على الـ 3 عوامل
#         model.fit(telemetry_buffer)
#         prediction = model.predict([features])
        
#         if prediction[0] == -1:
#             is_anomaly = 1
#             logging.warning(f"🚨 AI ANOMALY DETECTED AT {payload.location}! Gas: {payload.gas_level}ppm")

#     try:
#         conn = sqlite3.connect(DB_PATH, timeout=10)
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO telemetry (sensor_id, location, timestamp, temperature, humidity, gas_level, is_anomaly) VALUES (?, ?, ?, ?, ?, ?, ?)",
#             (payload.sensor_id, payload.location, payload.timestamp, payload.temperature, payload.humidity, payload.gas_level, is_anomaly)
#         )
#         conn.commit()
#         conn.close()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Database write failed")

#     return {"status": "success", "anomaly_detected": bool(is_anomaly)}



# import os
# import sqlite3
# import numpy as np
# import pandas as pd
# from fastapi import FastAPI
# from sklearn.ensemble import IsolationForest

# app = FastAPI()

# # Global memory buffer for the model
# telemetry_buffer = []
# model = IsolationForest(contamination=0.05, random_state=42)

# @app.post("/api/v1/telemetry")
# async def receive_telemetry(data: dict):
#     global telemetry_buffer, model
    
#     temp = data['temperature']
#     hum = data['humidity']
#     gas = data['gas_level']
    
#     # Append to buffer
#     telemetry_buffer.append([temp, hum, gas])
#     if len(telemetry_buffer) > 100:
#         telemetry_buffer.pop(0)
        
#     # Fit model if we have enough data
#     is_anomaly = 0
#     if len(telemetry_buffer) >= 10:
#         X = np.array(telemetry_buffer)
#         model.fit(X)
#         pred = model.predict([[temp, hum, gas]])[0] # -1 means anomaly, 1 means normal
        
#         # Hybrid check: ML flags it AND values are genuinely outside safe bounds
#         if pred == -1 and (temp > 30.0 or hum > 75.0 or gas > 2.0):
#             is_anomaly = 1

#     conn = sqlite3.connect("/app/data/smarta_v2.db")
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO telemetry (sensor_id, location, timestamp, temperature, humidity, gas_level, is_anomaly)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, (data['sensor_id'], data['location'], data['timestamp'], temp, hum, gas, is_anomaly))
#     conn.commit()
#     conn.close()
    
#     return {"status": "ok", "is_anomaly": is_anomaly}






# import os
# import sqlite3
# import numpy as np
# import pandas as pd
# from fastapi import FastAPI
# from sklearn.ensemble import IsolationForest
# from Backend.database import init_db, add_inventory_item, get_all_inventory, delete_inventory_item
# app = FastAPI()

# telemetry_buffer = []
# model = IsolationForest(contamination=0.05, random_state=42)

# # --- Database Initialization ---
# def init_db():
#     os.makedirs("/app/data", exist_ok=True)
#     conn = sqlite3.connect("/app/data/smarta_v2.db")
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS telemetry (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             sensor_id TEXT,
#             location TEXT,
#             timestamp TEXT,
#             temperature REAL,
#             humidity REAL,
#             gas_level REAL,
#             is_anomaly INTEGER
#         )
#     """)
#     conn.commit()
#     conn.close()

# init_db()  # Run once when server starts
# # -------------------------------

# @app.post("/api/v1/telemetry")
# async def receive_telemetry(data: dict):
#     global telemetry_buffer, model
    
#     # Cast values to float just to be 100% safe
#     temp = float(data['temperature'])
#     hum = float(data['humidity'])
#     gas = float(data['gas_level'])
    
#     is_anomaly = 0
    
#     if len(telemetry_buffer) >= 10:
#         X = np.array(telemetry_buffer)
#         model.fit(X)
#         pred = model.predict([[temp, hum, gas]])[0]
        
#         if pred == -1 and (temp > 30.0 or hum > 75.0 or gas > 2.0):
#             is_anomaly = 1
            
#     # Fail-safe override for catastrophic total failure
#     if temp > 40.0 and hum > 80.0 and gas > 5.0:
#         is_anomaly = 1

#     # Smart Buffer: Only append normal data to avoid Model Pollution
#     if is_anomaly == 0:
#         telemetry_buffer.append([temp, hum, gas])
#         if len(telemetry_buffer) > 100:
#             telemetry_buffer.pop(0)

#     conn = sqlite3.connect("/app/data/smarta_v2.db")
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO telemetry (sensor_id, location, timestamp, temperature, humidity, gas_level, is_anomaly)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, (data['sensor_id'], data['location'], data['timestamp'], temp, hum, gas, is_anomaly))
#     conn.commit()
#     conn.close()
    
#     return {"status": "ok", "is_anomaly": is_anomaly}


import os
import sqlite3
import warnings
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form
from sklearn.ensemble import IsolationForest

# Mute Scikit-Learn joblib thread/parallel warnings in terminal output
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Import database and vision helper modules (FIXED CASE SENSITIVITY)
# Import database and vision helper modules
from database import init_db, add_inventory_item, get_all_inventory, delete_inventory_item
from vision import analyze_image, predict_shelf_life

app = FastAPI(title="SMARTA Warehouse API")

telemetry_buffer = []
# Set n_jobs=1 to suppress joblib parallel worker noise on Windows/Python 3.13
model = IsolationForest(contamination=0.05, random_state=42, n_jobs=1)


def ensure_telemetry_schema(conn: sqlite3.Connection):
    """
    Ensures the telemetry table exists with all required columns,
    automatically adding any missing columns to prevent database crashes.
    """
    cursor = conn.cursor()
    cursor.execute("""
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
    """)
    
    # Check existing schema to dynamically alter/add missing columns if old DB exists
    cursor.execute("PRAGMA table_info(telemetry)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    required_columns = {
        "sensor_id": "TEXT",
        "location": "TEXT",
        "timestamp": "TEXT",
        "temperature": "REAL",
        "humidity": "REAL",
        "gas_level": "REAL",
        "is_anomaly": "INTEGER"
    }

    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            cursor.execute(f"ALTER TABLE telemetry ADD COLUMN {col_name} {col_type}")
            
    conn.commit()


# --- Startup Event ---
@app.on_event("startup")
def startup_event():
    init_db()
    conn = sqlite3.connect("smarta.db", timeout=10.0)
    ensure_telemetry_schema(conn)
    conn.close()


# --- Telemetry & Anomaly Processing ---
@app.post("/api/v1/telemetry")
def receive_telemetry(data: dict):
    """
    Receives IoT sensor telemetry data, runs Isolation Forest anomaly detection,
    and safely persists records into SQLite.
    """
    global telemetry_buffer, model

    try:
        temp = float(data.get('temperature', 0.0))
        hum = float(data.get('humidity', 0.0))
        gas = float(data.get('gas_level', 0.0))
        sensor_id = str(data.get('sensor_id', 'SENS-01'))
        location = str(data.get('location', 'Shelf A1'))
        timestamp = str(data.get('timestamp', ''))

        is_anomaly = 0

        # 1. Isolation Forest Machine Learning check
        if len(telemetry_buffer) >= 10:
            X = np.array(telemetry_buffer)
            model.fit(X)
            preds = model.predict([[temp, hum, gas]])
            
            # Robust extraction preventing tuple index out of range errors
            pred = preds.item() if hasattr(preds, 'item') else preds[0]
            if pred == -1 and (temp > 30.0 or hum > 75.0 or gas > 2.0):
                is_anomaly = 1

        # 2. Hard threshold override for extreme spoilage
        if temp > 40.0 and hum > 80.0 and gas > 2.5:
            is_anomaly = 1

        # 3. Telemetry buffer management (clean baseline data only)
        if is_anomaly == 0:
            telemetry_buffer.append([temp, hum, gas])
            if len(telemetry_buffer) > 100:
                telemetry_buffer.pop(0)

        # 4. Save safely to SQLite
        conn = sqlite3.connect("smarta.db", timeout=10.0)
        ensure_telemetry_schema(conn)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO telemetry (sensor_id, location, timestamp, temperature, humidity, gas_level, is_anomaly)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (sensor_id, location, timestamp, temp, hum, gas, is_anomaly))
        
        conn.commit()
        conn.close()

        return {"status": "ok", "is_anomaly": is_anomaly}

    except Exception as e:
        print(f"❌ Error handling telemetry: {e}")
        return {"status": "error", "message": str(e)}


# --- Veggie AI Scanner Endpoint ---
@app.post("/api/v1/scan-veggie")
async def scan_veggie(
    file: UploadFile = File(...),
    shelf_id: str = Form("Shelf A1")
):
    """
    Processes produce image with YOLOv8, models remaining shelf-life using Q10 decay,
    and automatically logs the item in inventory.
    """
    image_bytes = await file.read()
    detection = analyze_image(image_bytes)

    if not detection.get("detected"):
        return {
            "success": False,
            "message": "No recognizable produce detected. Please try a clearer image."
        }

    # Standard ambient warehouse microclimate baselines
    current_temp = 20.0
    current_hum = 60.0

    exp_info = predict_shelf_life(detection["primary_item"], current_temp, current_hum)

    db_id = add_inventory_item(
        item_name=exp_info["item"],
        shelf_id=shelf_id,
        confidence=detection["confidence"],
        days_remaining=exp_info["estimated_days_remaining"],
        exp_date=exp_info["estimated_expiration_date"],
        risk=exp_info["degradation_risk"]
    )

    return {
        "success": True,
        "inventory_id": db_id,
        "shelf_assigned": shelf_id,
        "detection": detection,
        "freshness_assessment": exp_info
    }


# --- Warehouse Inventory CRUD Endpoints ---
@app.get("/api/v1/inventory")
def fetch_inventory():
    """Returns all active warehouse produce inventory records."""
    items = get_all_inventory()
    return {"success": True, "inventory": items}


@app.delete("/api/v1/inventory/{item_id}")
def remove_inventory_item(item_id: int):
    """Deletes an item record from warehouse inventory."""
    delete_inventory_item(item_id)
    return {"success": True, "message": f"Item {item_id} successfully removed."}
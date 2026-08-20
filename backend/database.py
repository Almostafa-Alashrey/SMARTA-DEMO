# import sqlite3
# from typing import List, Dict, Any

# DB_PATH = "smarta.db"

# def init_db():
#     """Initializes the SQLite database tables if they do not exist."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
    
#     # Telemetry logs table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS telemetry (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             timestamp TEXT,
#             shelf_id TEXT,
#             temperature REAL,
#             humidity REAL,
#             methane_ppm REAL,
#             is_anomaly INTEGER
#         )
#     """)
    
#     # Inventory table for scanned produce
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS inventory (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item_name TEXT NOT NULL,
#             shelf_id TEXT NOT NULL,
#             confidence REAL,
#             days_remaining INTEGER,
#             expiration_date TEXT,
#             degradation_risk TEXT,
#             scanned_at TEXT DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
    
#     conn.commit()
#     conn.close()

# def add_inventory_item(item_name: str, shelf_id: str, confidence: float, days_remaining: int, exp_date: str, risk: str) -> int:
#     """Inserts a newly scanned produce item into SQLite."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO inventory (item_name, shelf_id, confidence, days_remaining, expiration_date, degradation_risk)
#         VALUES (?, ?, ?, ?, ?, ?)
#     """, (item_name, shelf_id, confidence, days_remaining, exp_date, risk))
    
#     item_id = cursor.lastrowid
#     conn.commit()
#     conn.close()
#     return item_id

# def get_all_inventory() -> List[Dict[str, Any]]:
#     """Retrieves all active inventory items."""
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM inventory ORDER BY id DESC")
#     rows = cursor.fetchall()
#     conn.close()
#     return [dict(row) for row in rows]

# def delete_inventory_item(item_id: int):
#     """Deletes an item from inventory when removed or consumed."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
#     conn.commit()
#     conn.close()

import sqlite3
from typing import List, Dict, Any

DB_PATH = "smarta.db"

def get_db_connection() -> sqlite3.Connection:
    """Returns a connection configured with a timeout to prevent locking under concurrent usage."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database tables and enables WAL mode for high concurrency."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Enable Write-Ahead Logging for multi-user read/write concurrency
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        
        # Telemetry logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                shelf_id TEXT,
                temperature REAL,
                humidity REAL,
                methane_ppm REAL,
                is_anomaly INTEGER
            )
        """)
        
        # Inventory table for scanned produce
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                shelf_id TEXT NOT NULL,
                confidence REAL,
                days_remaining INTEGER,
                expiration_date TEXT,
                degradation_risk TEXT,
                scanned_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_inventory_item(item_name: str, shelf_id: str, confidence: float, days_remaining: int, exp_date: str, risk: str) -> int:
    """Inserts a newly scanned produce item into SQLite safely."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (item_name, shelf_id, confidence, days_remaining, expiration_date, degradation_risk)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_name, shelf_id, confidence, days_remaining, exp_date, risk))
        
        item_id = cursor.lastrowid
        conn.commit()
        return item_id

def get_all_inventory() -> List[Dict[str, Any]]:
    """Retrieves all active inventory items concurrently."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def delete_inventory_item(item_id: int):
    """Deletes an item from inventory when removed or consumed."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
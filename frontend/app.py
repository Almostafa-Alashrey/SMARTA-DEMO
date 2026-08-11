import os
import time
import random
import sqlite3
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="SMARTA Dashboard", page_icon="🌱", layout="wide")
st.title("🌱 SMARTA: Intelligent Storage Management")

DB_PATH = os.getenv("DB_PATH", "/app/data/smarta.db")

def load_data():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 100", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

tab1, tab2, tab3 = st.tabs(["📊 Live Dashboard & Logs", "🥕 Veggie AI Scanner", "📦 Warehouse Inventory"])

with tab1:
    st.header("Real-Time Environment Metrics")
    if st.button("🔄 Refresh Data"):
        st.rerun()
        
    df = load_data()
    
    if not df.empty:
        df['timestamp_display'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
        latest = df.iloc[0]
        
        # عرض التنبيه بمكان الرف لو فيه مشكلة
        if latest['is_anomaly']:
            st.error(f"🚨 ALERT: Spoilage Risk Detected at **{latest['location']}**!")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Location", f"{latest['location']}")
        col2.metric("Temperature", f"{latest['temperature']} °C")
        col3.metric("Humidity", f"{latest['humidity']} %")
        col4.metric("Ethylene Gas", f"{latest['gas_level']} ppm")
        
        st.subheader("Temperature & Gas Trends")
        chart_data = df.set_index("timestamp_display")[["temperature", "gas_level"]]
        st.line_chart(chart_data)
        
        st.subheader("System Logs")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Waiting for data from IoT Simulator...")

with tab2:
    st.header("Veggie Quality Assessment")
    st.write("Upload a photo of a vegetable to check its quality and detect defects.")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        if st.button("Analyze Quality"):
            with st.spinner("AI is analyzing the image..."):
                time.sleep(2)
                results = ["🟢 Fresh - Excellent Quality", "🟡 Minor Blemishes - Good for immediate use", "🔴 Spoiled - Remove Immediately"]
                verdict = random.choice(results)
                if "Spoiled" in verdict:
                    st.error(f"Analysis Result: {verdict}")
                elif "Fresh" in verdict:
                    st.success(f"Analysis Result: {verdict}")
                else:
                    st.warning(f"Analysis Result: {verdict}")

with tab3:
    st.header("Warehouse Inventory Management")
    inventory_data = {
        "Item Name": ["Tomatoes", "Potatoes", "Carrots", "Onions", "Cucumbers"],
        "Quantity (kg)": [150, 500, 200, 300, 100],
        "Location": ["Shelf A1", "Shelf B2", "Shelf C3", "Shelf A2", "Shelf B1"],
        "Entry Date": ["2026-08-09", "2026-08-05", "2026-08-10", "2026-08-01", "2026-08-11"],
        "Expiry Date": ["2026-08-23", "2026-10-05", "2026-09-10", "2026-11-01", "2026-08-25"]
    }
    st.dataframe(pd.DataFrame(inventory_data), use_container_width=True)
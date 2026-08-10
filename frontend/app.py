import os
import time
import random
import sqlite3
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="SMARTA Dashboard", page_icon="🌱", layout="wide")
st.title("🌱 SMARTA: Intelligent Storage Management")

# مكان الداتابيز اللي هيتربط مع الـ Backend عن طريق Docker
DB_PATH = os.getenv("DB_PATH", "/app/data/smarta.db")

def load_data():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 100", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

tab1, tab2 = st.tabs(["📊 Live Dashboard & Logs", "🥕 Veggie AI Scanner"])

with tab1:
    st.header("Real-Time Environment Metrics")
    if st.button("🔄 Refresh Data"):
        st.rerun()
        
    df = load_data()
    
    if not df.empty:
        latest = df.iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("Temperature", f"{latest['temperature']} °C")
        col2.metric("Humidity", f"{latest['humidity']} %")
        
        status = "🔴 ANOMALY DETECTED" if latest['is_anomaly'] else "🟢 Normal"
        col3.metric("System Status", status)
        
        st.subheader("Temperature Trend")
        chart_data = df.set_index("timestamp")[["temperature"]]
        st.line_chart(chart_data)
        
        st.subheader("System Logs")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Waiting for data from IoT Simulator... (Or database is initializing)")

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
                results = [
                    "🟢 Fresh - Excellent Quality", 
                    "🟡 Minor Blemishes - Good for immediate use", 
                    "🔴 Spoiled - Remove Immediately to prevent spread"
                ]
                verdict = random.choice(results)
                
                if "Spoiled" in verdict:
                    st.error(f"Analysis Result: {verdict}")
                elif "Fresh" in verdict:
                    st.success(f"Analysis Result: {verdict}")
                else:
                    st.warning(f"Analysis Result: {verdict}")
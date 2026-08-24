import os
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="SMARTA Dashboard", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

# --- Global Configs ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- Initialize Session State for Notifications & Initial Load ---
if "notified_items" not in st.session_state:
    st.session_state.notified_items = set()

if "initial_load_done" not in st.session_state:
    st.session_state.initial_load_done = False

# --- Cached Data Fetchers (Lightweight & Fast) ---
@st.cache_data(ttl=10) # Caches inventory for 10s to prevent API spam
def fetch_inventory_cached():
    try:
        res = requests.get(f"{BACKEND_URL}/api/v1/inventory", timeout=2).json()
        if res.get("success") and res.get("inventory"):
            return res["inventory"]
    except Exception:
        pass
    return []

@st.cache_data(ttl=5) # Caches telemetry for 5s
def fetch_telemetry_cached():
    try:
        res = requests.get(f"{BACKEND_URL}/api/v1/telemetry", timeout=2).json()
        if res.get("success") and res.get("telemetry"):
            return pd.DataFrame(res["telemetry"])
    except Exception:
        pass
    return pd.DataFrame()

# --- Professional Dark Glassmorphism Styling ---
st.markdown("""
<style>
    .pill-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .safe-badge { background-color: #064e3b; color: #34d399; border: 1px solid #059669; }
    .alert-badge { background-color: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
    }
    .glass-label { font-size: 14px; color: #9ca3af; font-weight: 600; text-transform: uppercase; }
    .glass-value { font-size: 30px; font-weight: 700; margin: 8px 0; color: #f3f4f6; }

    [data-testid="stSidebar"] button {
        background-color: #1f2937 !important;
        color: #34d399 !important;
        border: 1px solid #059669 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: #059669 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌱 SMARTA: Storage Monitoring & Real-time Tracking Assurance")
st.caption("AI-driven produce freshness prediction, microclimate anomaly detection, and automated shelf management.")

# ==========================================
# SIDEBAR: CONTROLLED NOTIFICATION CENTER
# ==========================================
st.sidebar.title("🔔 Notification Center")
st.sidebar.markdown("---")

sidebar_alerts = []

# Process Inventory Expiry Alerts without Flooding
inventory_data = fetch_inventory_cached()
for item in inventory_data:
    days_left = item.get("days_remaining", 99)
    item_name = item.get("item_name", "Item")
    shelf = item.get("shelf_id", "Shelf")
    item_id = item.get("id", item_name)

    if days_left <= 3:
        alert_text = f"⏳ **{item_name}** ({shelf}) expires in {days_left} day(s)!"
        sidebar_alerts.append(alert_text)
        
        toast_key = f"expiry_{item_id}_{days_left}"
        if st.session_state.initial_load_done and toast_key not in st.session_state.notified_items:
            st.toast(alert_text, icon="⚠️")
            st.session_state.notified_items.add(toast_key)
        elif not st.session_state.initial_load_done:
            st.session_state.notified_items.add(toast_key)

# Process Telemetry Microclimate Alerts
telemetry_df = fetch_telemetry_cached()
if not telemetry_df.empty:
    latest = telemetry_df.iloc[0]
    temp = latest.get("temperature", 0.0)
    hum = latest.get("humidity", 0.0)
    gas = latest.get("gas_level", 0.0)
    loc = latest.get("location", "Warehouse")
    is_anomaly = latest.get("is_anomaly", 0)
    
    if is_anomaly == 1:
        if temp > 30.0:
            sidebar_alerts.append(f"🌡️ High Temp at {loc}: {temp}°C")
        if hum > 75.0:
            sidebar_alerts.append(f"💧 High Humidity at {loc}: {hum}%")
        if gas > 1000.0:
            sidebar_alerts.append(f"☁️ Gas Spike at {loc}: {gas} PPM")

st.session_state.initial_load_done = True

# Render Sidebar Notification Feed
if sidebar_alerts:
    st.sidebar.error(f"Active Alerts: {len(sidebar_alerts)}")
    for alert in sidebar_alerts:
        st.sidebar.markdown(alert)
else:
    st.sidebar.success("🟢 All systems nominal. No active warnings.")

if st.sidebar.button("🧹 Clear Notification Cache"):
    st.session_state.notified_items.clear()
    st.cache_data.clear()
    st.rerun()

# --- Spline Chart Helper ---
def plot_spline_chart(df, y_col, color_hex, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df[y_col],
        mode='lines',
        line=dict(color=color_hex, width=3, shape='spline'),
        fill='tozeroy',
        fillcolor=f"rgba({int(color_hex[1:3], 16)}, {int(color_hex[3:5], 16)}, {int(color_hex[5:7], 16)}, 0.15)",
        name=title
    ))
    fig.update_layout(
        height=240, margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        font=dict(color="#9ca3af")
    )
    return fig

# --- Main Navigation Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Dashboard", "🥕 Veggie AI Scanner", "📦 Inventory", "🛠️ System Logs"])

# ==========================================
# TAB 1: LIVE DASHBOARD
# ==========================================
with tab1:
    df = fetch_telemetry_cached()
    
    if not df.empty and 'location' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', errors='coerce').dt.tz_localize(None)
        
        c_nav1, c_nav2 = st.columns([1, 4])
        with c_nav1:
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.rerun()
        with c_nav2:
            locations = list(df['location'].unique())
            selected_loc = st.selectbox("Select Active Shelf Node", locations, label_visibility="collapsed")
            
        display_df = df[df['location'] == selected_loc].copy()
        
        if not display_df.empty:
            latest = display_df.iloc[0]
            
            if latest.get('is_anomaly', 0) == 1:
                badge = f'<div class="pill-badge alert-badge">⚠️ ALERT [{selected_loc}]: Microclimate Anomaly Detected!</div>'
            else:
                badge = f'<div class="pill-badge safe-badge">✅ NORMAL [{selected_loc}]: Microclimate stable.</div>'
            st.markdown(badge, unsafe_allow_html=True)

            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(f'<div class="glass-card"><div class="glass-label">Node</div><div class="glass-value">{latest["location"]}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="glass-card"><div class="glass-label">Temperature</div><div class="glass-value">{latest["temperature"]} °C</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="glass-card"><div class="glass-label">Humidity</div><div class="glass-value">{latest["humidity"]} %</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="glass-card"><div class="glass-label">Gas Level</div><div class="glass-value">{latest["gas_level"]} ppm</div></div>', unsafe_allow_html=True)

            st.write("<br>", unsafe_allow_html=True)

            ch1, ch2, ch3 = st.columns(3)
            with ch1:
                st.subheader("Temperature Trend")
                st.plotly_chart(plot_spline_chart(display_df, 'temperature', '#f87171', 'Temp'), use_container_width=True)
            with ch2:
                st.subheader("Humidity Trend")
                st.plotly_chart(plot_spline_chart(display_df, 'humidity', '#60a5fa', 'Humidity'), use_container_width=True)
            with ch3:
                st.subheader("Gas Level Trend")
                st.plotly_chart(plot_spline_chart(display_df, 'gas_level', '#34d399', 'Gas'), use_container_width=True)
    else:
        st.info("Waiting for data from IoT Simulator...")

# ==========================================
# TAB 2: VEGGIE AI SCANNER
# ==========================================
with tab2:
    st.header("🥕 Veggie AI Scanner & Freshness Predictor")
    
    input_mode = st.radio("Select Image Input Source:", ["📷 Snap Photo", "📁 Upload Image File"], horizontal=True)
    selected_shelf = st.selectbox("Assign Shelf Location", ["Shelf A1", "Shelf B2", "Shelf C3"])

    uploaded_file = None
    if input_mode == "📷 Snap Photo":
        uploaded_file = st.camera_input("Take a picture of the produce")
    else:
        uploaded_file = st.file_uploader("Choose a produce image...", type=["jpg", "jpeg", "png"])

    if uploaded_file and st.button("🔍 Run AI Diagnostics"):
        with st.spinner("Processing image via AI model..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"shelf_id": selected_shelf}
                res = requests.post(f"{BACKEND_URL}/api/v1/scan-veggie", files=files, data=data).json()
                
                if res.get("success"):
                    st.success("✅ Item successfully identified and assigned!")
                    freshness = res.get("freshness_assessment", {})
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("📦 Detected Produce", freshness.get("item"))
                    c2.metric("⏳ Est. Days Remaining", f"{freshness.get('estimated_days_remaining')} Days")
                    c3.metric("📅 Expiration Date", freshness.get("estimated_expiration_date"))
                    
                    st.cache_data.clear() # Clear cache so inventory updates immediately
                else:
                    st.warning(res.get("message", "No item detected."))
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# TAB 3: INVENTORY
# ==========================================
with tab3:
    st.header("📦 Warehouse Inventory")
    inv_items = fetch_inventory_cached()
    if inv_items:
        st.dataframe(pd.DataFrame(inv_items), use_container_width=True)
    else:
        st.info("Inventory is empty.")

# ==========================================
# TAB 4: SYSTEM LOGS
# ==========================================
with tab4:
    st.header("🛠️ Telemetry Logs")
    df_logs = fetch_telemetry_cached()
    if not df_logs.empty:
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No logs available.")
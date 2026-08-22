import os
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="SMARTA Dashboard", page_icon="🌱", layout="wide")

# --- Global Configs ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- Glassmorphism & UI Styling ---
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
    .safe-badge { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
    .alert-badge { background-color: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 20px;
    }
    .glass-label { font-size: 14px; color: #777; font-weight: 600; text-transform: uppercase; }
    .glass-value { font-size: 30px; font-weight: 700; margin: 8px 0; }
    .trend-up { color: #ff6b6b; font-size: 13px; font-weight: 600; }
    .trend-down { color: #20c997; font-size: 13px; font-weight: 600; }
    .trend-stable { color: #888; font-size: 13px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.title("🌱 SMARTA: Storage Monitoring & Real-time Tracking Assurance")
st.caption("AI-driven produce freshness prediction, microclimate anomaly detection, and automated shelf management.")

# --- Data Loader ---
def load_telemetry_data():
    try:
        res = requests.get(f"{BACKEND_URL}/api/v1/telemetry").json()
        if res.get("success") and res.get("telemetry"):
            return pd.DataFrame(res["telemetry"])
    except Exception:
        pass
    return pd.DataFrame()

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
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.1)')
    )
    return fig

# --- Main Navigation Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Dashboard", "🥕 Veggie AI Scanner", "📦 Inventory", "🛠️ System Logs"])

# ==========================================
# TAB 1: LIVE DASHBOARD
# ==========================================
with tab1:
    df = load_telemetry_data()
    
    if not df.empty and 'location' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        c_nav1, c_nav2 = st.columns([1, 4])
        with c_nav1:
            if st.button("🔄 Refresh Telemetry", use_container_width=True):
                st.rerun()
        with c_nav2:
            locations = list(df['location'].unique())
            selected_loc = st.selectbox("Select Active Shelf Node", locations, label_visibility="collapsed")
            
        display_df = df[df['location'] == selected_loc].copy()
        
        if not display_df.empty:
            latest = display_df.iloc[0]
            
            # Alert Pill Badge
            if latest.get('is_anomaly', 0) == 1:
                badge = f'<div class="pill-badge alert-badge">⚠️ ALERT [{selected_loc}]: Microclimate Anomaly Detected — High Temp/Gas Level!</div>'
            else:
                badge = f'<div class="pill-badge safe-badge">✅ NORMAL [{selected_loc}]: Storage microclimate within nominal parameters.</div>'
            st.markdown(badge, unsafe_allow_html=True)

            # KPI Cards
            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(f'<div class="glass-card"><div class="glass-label">Node</div><div class="glass-value">{latest["location"]}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="glass-card"><div class="glass-label">Temperature</div><div class="glass-value">{latest["temperature"]} °C</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="glass-card"><div class="glass-label">Humidity</div><div class="glass-value">{latest["humidity"]} %</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="glass-card"><div class="glass-label">Methane</div><div class="glass-value">{latest["gas_level"]} ppm</div></div>', unsafe_allow_html=True)

            st.write("<br>", unsafe_allow_html=True)

            # Spline Charts
            ch1, ch2, ch3 = st.columns(3)
            with ch1:
                st.subheader("Temperature Trend")
                st.plotly_chart(plot_spline_chart(display_df, 'temperature', '#ff6b6b', 'Temp'), use_container_width=True)
            with ch2:
                st.subheader("Humidity Trend")
                st.plotly_chart(plot_spline_chart(display_df, 'humidity', '#339af0', 'Humidity'), use_container_width=True)
            with ch3:
                st.subheader("Methane Gas Trend")
                st.plotly_chart(plot_spline_chart(display_df, 'gas_level', '#20c997', 'Methane'), use_container_width=True)
    else:
        st.info("Waiting for data from IoT Simulator... (Ensure Backend & Simulator are running)")

# ==========================================
# TAB 2: VEGGIE AI SCANNER
# ==========================================
with tab2:
    st.header("🥕 Veggie AI Scanner & Freshness Predictor")
    
    input_mode = st.radio("Select Image Input Source:", ["📷 Live Camera Capture", "📁 Upload Image File"], horizontal=True)
    
    uploaded_file = None
    if input_mode == "📷 Live Camera Capture":
        uploaded_file = st.camera_input("Take a picture of the produce/shelf")
    else:
        uploaded_file = st.file_uploader("Choose a produce image...", type=["jpg", "jpeg", "png"])

    selected_shelf = st.selectbox("Assign Shelf Location", ["Shelf A1", "Shelf B2", "Shelf C3"])

    if uploaded_file and st.button("🔍 Run AI Diagnostics"):
        with st.spinner("Processing image via AI model..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"shelf_id": selected_shelf}
                res = requests.post(f"{BACKEND_URL}/api/v1/scan-veggie", files=files, data=data).json()
                
                if res.get("success"):
                    st.success(f"✅ Item successfully assigned to **{res.get('shelf_assigned', selected_shelf)}**!")
                    
                    freshness = res.get("freshness_assessment", {})
                    c1, c2, c3 = st.columns(3)
                    c1.metric("📦 Detected Produce", freshness.get("item", "Unknown Produce"))
                    c2.metric("⏳ Est. Days Remaining", f"{freshness.get('estimated_days_remaining', 'N/A')} Days")
                    c3.metric("📅 Expiration Date", freshness.get("estimated_expiration_date", "N/A"))
                else:
                    st.warning(res.get("message", "No item detected in image."))
            except Exception as e:
                st.error(f"Backend Connection Error: {e}")

# ==========================================
# TAB 3: INVENTORY
# ==========================================
with tab3:
    st.header("📦 Warehouse Inventory")
    if st.button("🔄 Refresh Inventory", use_container_width=True):
        st.rerun()
        
    try:
        res = requests.get(f"{BACKEND_URL}/api/v1/inventory").json()
        if res.get("success") and res.get("inventory"):
            st.dataframe(pd.DataFrame(res["inventory"]), use_container_width=True)
        else:
            st.info("Inventory is currently empty.")
    except Exception as e:
        st.error(f"Failed to fetch inventory: {e}")

# ==========================================
# TAB 4: SYSTEM LOGS
# ==========================================
with tab4:
    st.header("🛠️ Telemetry Logs")
    df_logs = load_telemetry_data()
    if not df_logs.empty:
        st.dataframe(df_logs, use_container_width=True)
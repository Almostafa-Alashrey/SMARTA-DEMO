# import os
# import time
# import random
# import sqlite3
# import pandas as pd
# import streamlit as st
# from PIL import Image

# st.set_page_config(page_title="SMARTA Dashboard", page_icon="🌱", layout="wide")
# st.title("🌱 SMARTA: Intelligent Storage Management")

# DB_PATH = os.getenv("DB_PATH", "/app/data/smarta_v2.db")

# def load_data():
#     try:
#         conn = sqlite3.connect(DB_PATH, timeout=10)
#         df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 300", conn)
#         conn.close()
#         return df
#     except Exception as e:
#         return pd.DataFrame()

# tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Dashboard", "🥕 Veggie AI Scanner", "📦 Inventory", "🛠️ System Logs"])

# with tab1:
#     df = load_data()
    
#     if not df.empty:
#         # ضبط التوقيت ليكون بتوقيت مصر (Cairo Time) عشان الجرافات
#         df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', utc=True).dt.tz_convert('Africa/Cairo').dt.tz_localize(None)        
#         col_refresh, col_selector = st.columns([1, 4])
#         with col_refresh:
#             if st.button("🔄 Refresh Data", use_container_width=True):
#                 st.rerun()
                
#         locations = list(df['location'].unique())
#         with col_selector:
#             selected_loc = st.selectbox("📍 Select View", locations, label_visibility="collapsed")
            
#         st.markdown("---")
        
#         display_df = df[df['location'] == selected_loc].copy()
        
#         if not display_df.empty:
#             latest = display_df.iloc[0]
            
#             if latest['is_anomaly'] == 1:
#                 st.error(f"🚨 **CRITICAL ALERT:** Abnormal environmental trends detected at **{selected_loc}**. Potential spoilage!")
#             else:
#                 st.success(f"✅ **ALL CLEAR:** Storage conditions are optimal at **{selected_loc}**.")
            
#             c1, c2, c3, c4 = st.columns(4)
#             c1.metric("Location", f"{latest['location']}")
#             c2.metric("Temperature", f"{latest['temperature']} °C")
#             c3.metric("Humidity", f"{latest['humidity']} %")
            
#             # تحويل رقم الغاز إلى كلمات إنجليزية
#             gas_val = latest['gas_level']
#             if gas_val < 1.0:
#                 gas_status = "Low"
#             elif gas_val < 3.0:
#                 gas_status = "Medium"
#             else:
#                 gas_status = "High"
                
#             c4.metric("Methane Concentration", gas_status)
            
#             st.markdown("<br>", unsafe_allow_html=True)
#             st.subheader(f"📈 Environmental Trends ({selected_loc})")
            
#             chart_tab1, chart_tab2, chart_tab3 = st.tabs(["🌡️ Temperature", "💧 Humidity", "☁️ Methane"])
#             chart_data = display_df.set_index("timestamp")
            
#             with chart_tab1: st.line_chart(chart_data[["temperature"]], color="#ff4b4b")
#             with chart_tab2: st.line_chart(chart_data[["humidity"]], color="#0068c9")
#             with chart_tab3: st.line_chart(chart_data[["gas_level"]], color="#29b09d")
#     else:
#         st.info("Waiting for data from IoT Simulator...")

# with tab2:
#     st.header("Veggie Quality Assessment")
#     st.write("Upload a photo of a vegetable to check its quality and detect defects.")
#     uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
#     if uploaded_file is not None:
#         image = Image.open(uploaded_file)
#         st.image(image, caption="Uploaded Image", use_column_width=True)
#         if st.button("Analyze Quality"):
#             with st.spinner("AI is analyzing the image..."):
#                 time.sleep(2)
#                 verdict = random.choice(["🟢 Fresh - Excellent Quality", "🟡 Minor Blemishes - Good for immediate use", "🔴 Spoiled - Remove Immediately"])
#                 if "Spoiled" in verdict: st.error(f"Analysis Result: {verdict}")
#                 elif "Fresh" in verdict: st.success(f"Analysis Result: {verdict}")
#                 else: st.warning(f"Analysis Result: {verdict}")

# with tab3:
#     st.header("Warehouse Inventory Management")
#     inventory_data = {
#         "Item Name": ["Tomatoes", "Potatoes", "Carrots", "Onions", "Cucumbers"],
#         "Quantity (kg)": [150, 500, 200, 300, 100],
#         "Location": ["Shelf A1", "Shelf B2", "Shelf C3", "Shelf A2", "Shelf B1"],
#         "Entry Date": ["2026-08-09", "2026-08-05", "2026-08-10", "2026-08-01", "2026-08-11"],
#         "Expiry Date": ["2026-08-23", "2026-10-05", "2026-09-10", "2026-11-01", "2026-08-25"]
#     }
#     st.dataframe(pd.DataFrame(inventory_data), use_container_width=True)

# with tab4:
#     st.header("System Telemetry Logs")
#     if not df.empty: st.dataframe(df, use_container_width=True)




# import os
# import time
# import random
# import sqlite3
# import pandas as pd
# import streamlit as st
# import plotly.graph_objects as go
# from PIL import Image

# st.set_page_config(page_title="SMARTA Dashboard", page_icon="🌱", layout="wide")

# # --- Global CSS for Glassmorphism & Badges ---
# st.markdown("""
# <style>
#     .pill-badge {
#         display: inline-block;
#         padding: 8px 16px;
#         border-radius: 50px;
#         font-weight: 600;
#         font-size: 14px;
#         margin-bottom: 20px;
#         box-shadow: 0 2px 5px rgba(0,0,0,0.05);
#     }
#     .safe-badge {
#         background-color: #e8f5e9;
#         color: #2e7d32;
#         border: 1px solid #a5d6a7;
#     }
#     .alert-badge {
#         background-color: #ffebee;
#         color: #c62828;
#         border: 1px solid #ef9a9a;
#     }
    
#     .glass-card {
#         background: rgba(255, 255, 255, 0.05);
#         backdrop-filter: blur(10px);
#         -webkit-backdrop-filter: blur(10px);
#         border: 1px solid rgba(128, 128, 128, 0.2);
#         border-radius: 16px;
#         padding: 20px;
#         box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
#     }
#     .glass-label {
#         font-size: 14px;
#         color: #777;
#         display: flex;
#         align-items: center;
#         gap: 8px;
#         font-weight: 600;
#         text-transform: uppercase;
#         letter-spacing: 0.5px;
#     }
#     .glass-value {
#         font-size: 32px;
#         font-weight: 700;
#         margin: 10px 0 5px 0;
#         color: inherit;
#     }
#     .trend-up { color: #ff6b6b; font-size: 13px; font-weight: 600; }
#     .trend-down { color: #20c997; font-size: 13px; font-weight: 600; }
#     .trend-stable { color: #888; font-size: 13px; font-weight: 600; }
# </style>
# """, unsafe_allow_html=True)

# st.title("🌱 SMARTA: Intelligent Storage Management")

# DB_PATH = os.getenv("DB_PATH", "/app/data/smarta_v2.db")

# def load_data():
#     try:
#         conn = sqlite3.connect(DB_PATH, timeout=10)
#         df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 300", conn)
#         conn.close()
#         return df
#     except Exception as e:
#         return pd.DataFrame()

# # Helper function to plot smooth Spline charts with gradients
# def plot_spline_chart(df, y_col, color_hex, title):
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=df['timestamp'], y=df[y_col],
#         mode='lines',
#         line=dict(color=color_hex, width=3, shape='spline'),
#         fill='tozeroy',
#         fillcolor=f"rgba({int(color_hex[1:3], 16)}, {int(color_hex[3:5], 16)}, {int(color_hex[5:7], 16)}, 0.2)",
#         name=title
#     ))
#     fig.update_layout(
#         height=250, margin=dict(l=0, r=0, t=10, b=0),
#         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
#         xaxis=dict(showgrid=False, zeroline=False, visible=False),
#         yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.1)', zeroline=False)
#     )
#     return fig

# tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Dashboard", "🥕 Veggie AI Scanner", "📦 Inventory", "🛠️ System Logs"])

# with tab1:
#     df = load_data()
    
#     if not df.empty:
#         df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', utc=True).dt.tz_convert('Africa/Cairo').dt.tz_localize(None)        
        
#         # --- Top Navigation Bar for Controls ---
#         nav_col1, nav_col2, nav_col3 = st.columns([1.5, 3, 5])
#         with nav_col1:
#             if st.button("🔄 Refresh Data", use_container_width=True):
#                 st.experimental_rerun()
        
#         locations = list(df['location'].unique())
#         with nav_col2:
#             selected_loc = st.selectbox("Select Shelf", locations, label_visibility="collapsed")
            
#         st.markdown("<br>", unsafe_allow_html=True)
        
#         display_df = df[df['location'] == selected_loc].copy()
        
#         if not display_df.empty:
#             latest = display_df.iloc[0]
#             # Calculate simple trend based on the 10th latest record (or last available)
#             prev = display_df.iloc[min(10, len(display_df)-1)]
            
#             temp_diff = latest['temperature'] - prev['temperature']
#             hum_diff = latest['humidity'] - prev['humidity']
            
#             # --- Alert Pill Badge ---
#             if latest['is_anomaly'] == 1:
#                 issues, actions = [], []
#                 if latest['temperature'] > 30.0: issues.append("High Temp"); actions.append("Check AC")
#                 if latest['humidity'] > 75.0: issues.append("High Humidity"); actions.append("Ventilate")
#                 if latest['gas_level'] > 2.0: issues.append("High Methane"); actions.append("Isolate Spoilage")
                
#                 issue_text = " & ".join(issues) if issues else "Irregular Patterns"
#                 action_text = " | ".join(actions) if actions else "Manual Inspection Required"
                
#                 badge_html = f'<div class="pill-badge alert-badge"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 5px;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg> CRITICAL [{selected_loc}]: {issue_text} — Action: {action_text}</div>'
#             else:
#                 badge_html = f'<div class="pill-badge safe-badge"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 5px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg> ALL CLEAR: Conditions optimal at {selected_loc}</div>'
                
#             st.markdown(badge_html, unsafe_allow_html=True)
            
#             # --- Glassmorphism KPI Cards ---
#             c1, c2, c3, c4 = st.columns(4)
            
#             # Icons SVG (Lucide)
#             icon_map = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"></path><circle cx="12" cy="10" r="3"></circle></svg>'
#             icon_temp = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff6b6b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path></svg>'
#             icon_hum = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#339af0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22a5 5 0 0 0 5-5c0-2-5-10-5-10S7 15 7 17a5 5 0 0 0 5 5z"></path></svg>'
#             icon_gas = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#20c997" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-8h1.79a4.5 4.5 0 1 1 0 9Z"></path></svg>'

#             # Formatting Trend
#             def get_trend_html(val):
#                 if abs(val) < 0.2: return f'<span class="trend-stable">~ Stable vs last</span>'
#                 if val > 0: return f'<span class="trend-up">↑ +{val:.1f} vs last</span>'
#                 return f'<span class="trend-down">↓ {val:.1f} vs last</span>'

#             with c1:
#                 st.markdown(f'''
#                     <div class="glass-card">
#                         <div class="glass-label">{icon_map} Location</div>
#                         <div class="glass-value">{latest['location']}</div>
#                         <div class="trend-stable">Active Sensor Node</div>
#                     </div>
#                 ''', unsafe_allow_html=True)
                
#             with c2:
#                 st.markdown(f'''
#                     <div class="glass-card">
#                         <div class="glass-label">{icon_temp} Temperature</div>
#                         <div class="glass-value">{latest['temperature']} <span style="font-size:16px;">°C</span></div>
#                         {get_trend_html(temp_diff)}
#                     </div>
#                 ''', unsafe_allow_html=True)
                
#             with c3:
#                 st.markdown(f'''
#                     <div class="glass-card">
#                         <div class="glass-label">{icon_hum} Humidity</div>
#                         <div class="glass-value">{latest['humidity']} <span style="font-size:16px;">%</span></div>
#                         {get_trend_html(hum_diff)}
#                     </div>
#                 ''', unsafe_allow_html=True)
                
#             with c4:
#                 gas_val = latest['gas_level']
#                 gas_status, trend = ("Low", "trend-down") if gas_val < 1.0 else ("Medium", "trend-stable") if gas_val < 3.0 else ("High", "trend-up")
#                 st.markdown(f'''
#                     <div class="glass-card">
#                         <div class="glass-label">{icon_gas} Methane</div>
#                         <div class="glass-value">{gas_status}</div>
#                         <div class="{trend}">Current: {gas_val:.2f} ppm</div>
#                     </div>
#                 ''', unsafe_allow_html=True)
            
#             st.markdown("<br>", unsafe_allow_html=True)
            
#             # --- Smooth Spline Charts with Gradients ---
#             chart_col1, chart_col2, chart_col3 = st.columns(3)
            
#             with chart_col1:
#                 st.markdown('<div class="glass-label" style="margin-bottom:10px;">Temperature Trend</div>', unsafe_allow_html=True)
#                 st.plotly_chart(plot_spline_chart(display_df, 'temperature', '#ff6b6b', 'Temp'), use_container_width=True, config={'displayModeBar': False})
                
#             with chart_col2:
#                 st.markdown('<div class="glass-label" style="margin-bottom:10px;">Humidity Trend</div>', unsafe_allow_html=True)
#                 st.plotly_chart(plot_spline_chart(display_df, 'humidity', '#339af0', 'Humidity'), use_container_width=True, config={'displayModeBar': False})
                
#             with chart_col3:
#                 st.markdown('<div class="glass-label" style="margin-bottom:10px;">Methane Concentration</div>', unsafe_allow_html=True)
#                 st.plotly_chart(plot_spline_chart(display_df, 'gas_level', '#20c997', 'Methane'), use_container_width=True, config={'displayModeBar': False})
                
#     else:
#         st.info("Waiting for data from IoT Simulator...")

# with tab2:
#     st.header("Veggie Quality Assessment")
#     st.write("Upload a photo of a vegetable to check its quality and detect defects.")
#     uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
#     if uploaded_file is not None:
#         image = Image.open(uploaded_file)
#         st.image(image, caption="Uploaded Image", use_column_width=True)
#         if st.button("Analyze Quality"):
#             with st.spinner("AI is analyzing the image..."):
#                 time.sleep(2)
#                 verdict = random.choice(["🟢 Fresh - Excellent Quality", "🟡 Minor Blemishes - Good for immediate use", "🔴 Spoiled - Remove Immediately"])
#                 if "Spoiled" in verdict: st.error(f"Analysis Result: {verdict}")
#                 elif "Fresh" in verdict: st.success(f"Analysis Result: {verdict}")
#                 else: st.warning(f"Analysis Result: {verdict}")

# with tab3:
#     st.header("Warehouse Inventory Management")
#     inventory_data = {
#         "Item Name": ["Tomatoes", "Potatoes", "Carrots", "Onions", "Cucumbers"],
#         "Quantity (kg)": [150, 500, 200, 300, 100],
#         "Location": ["Shelf A1", "Shelf B2", "Shelf C3", "Shelf A2", "Shelf B1"],
#         "Entry Date": ["2026-08-09", "2026-08-05", "2026-08-10", "2026-08-01", "2026-08-11"],
#         "Expiry Date": ["2026-08-23", "2026-10-05", "2026-09-10", "2026-11-01", "2026-08-25"]
#     }
#     st.dataframe(pd.DataFrame(inventory_data), use_container_width=True)

# with tab4:
#     st.header("System Telemetry Logs")
#     if not df.empty: st.dataframe(df, use_container_width=True)


# import os
# import sqlite3
# import requests
# import pandas as pd
# import streamlit as st
# import plotly.graph_objects as go

# # --- Page Configuration ---
# st.set_page_config(page_title="SMARTA Dashboard", page_icon="🌱", layout="wide")

# # --- Global Configs ---
# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# DB_PATH = os.getenv("DB_PATH", "smarta.db")

# # --- Glassmorphism & UI Styling ---
# st.markdown("""
# <style>
#     .pill-badge {
#         display: inline-block;
#         padding: 8px 16px;
#         border-radius: 50px;
#         font-weight: 600;
#         font-size: 14px;
#         margin-bottom: 20px;
#     }
#     .safe-badge { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
#     .alert-badge { background-color: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
#     .glass-card {
#         background: rgba(255, 255, 255, 0.05);
#         border: 1px solid rgba(128, 128, 128, 0.2);
#         border-radius: 16px;
#         padding: 20px;
#     }
#     .glass-label { font-size: 14px; color: #777; font-weight: 600; text-transform: uppercase; }
#     .glass-value { font-size: 30px; font-weight: 700; margin: 8px 0; }
#     .trend-up { color: #ff6b6b; font-size: 13px; font-weight: 600; }
#     .trend-down { color: #20c997; font-size: 13px; font-weight: 600; }
#     .trend-stable { color: #888; font-size: 13px; font-weight: 600; }
# </style>
# """, unsafe_allow_html=True)

# st.title("🌱 SMARTA: Storage Monitoring & Real-time Tracking Assurance")
# st.caption("AI-driven produce freshness prediction, microclimate anomaly detection, and automated shelf management.")

# # --- Data Loader ---
# def load_telemetry_data():
#     try:
#         if not os.path.exists(DB_PATH):
#             return pd.DataFrame()
#         conn = sqlite3.connect(DB_PATH, timeout=5)
#         df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY id DESC LIMIT 300", conn)
#         conn.close()
#         return df
#     except Exception:
#         return pd.DataFrame()

# def plot_spline_chart(df, y_col, color_hex, title):
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x=df['timestamp'], y=df[y_col],
#         mode='lines',
#         line=dict(color=color_hex, width=3, shape='spline'),
#         fill='tozeroy',
#         fillcolor=f"rgba({int(color_hex[1:3], 16)}, {int(color_hex[3:5], 16)}, {int(color_hex[5:7], 16)}, 0.15)",
#         name=title
#     ))
#     fig.update_layout(
#         height=240, margin=dict(l=0, r=0, t=10, b=0),
#         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
#         xaxis=dict(showgrid=False, visible=False),
#         yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.1)')
#     )
#     return fig

# # --- Main Navigation Tabs ---
# tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Dashboard", "🥕 Veggie AI Scanner", "📦 Inventory", "🛠️ System Logs"])

# # ==========================================
# # TAB 1: LIVE DASHBOARD
# # ==========================================
# with tab1:
#     df = load_telemetry_data()
    
#     if not df.empty and 'location' in df.columns:
#         df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', errors='coerce').dt.tz_localize(None)
        
#         c_nav1, c_nav2 = st.columns([1, 4])
#         with c_nav1:
#             if st.button("🔄 Refresh Telemetry", use_container_width=True):
#                 st.rerun()
#         with c_nav2:
#             locations = list(df['location'].unique())
#             selected_loc = st.selectbox("Select Active Shelf Node", locations, label_visibility="collapsed")
            
#         display_df = df[df['location'] == selected_loc].copy()
        
#         if not display_df.empty:
#             latest = display_df.iloc[0]
            
#             # Alert Pill Badge
#             if latest.get('is_anomaly', 0) == 1:
#                 badge = f'<div class="pill-badge alert-badge">⚠️ ALERT [{selected_loc}]: Microclimate Anomaly Detected — High Temp/Gas Level!</div>'
#             else:
#                 badge = f'<div class="pill-badge safe-badge">✅ NORMAL [{selected_loc}]: Storage microclimate within nominal parameters.</div>'
#             st.markdown(badge, unsafe_allow_html=True)

#             # KPI Cards
#             k1, k2, k3, k4 = st.columns(4)
#             k1.markdown(f'<div class="glass-card"><div class="glass-label">Node</div><div class="glass-value">{latest["location"]}</div></div>', unsafe_allow_html=True)
#             k2.markdown(f'<div class="glass-card"><div class="glass-label">Temperature</div><div class="glass-value">{latest["temperature"]} °C</div></div>', unsafe_allow_html=True)
#             k3.markdown(f'<div class="glass-card"><div class="glass-label">Humidity</div><div class="glass-value">{latest["humidity"]} %</div></div>', unsafe_allow_html=True)
#             k4.markdown(f'<div class="glass-card"><div class="glass-label">Methane</div><div class="glass-value">{latest["gas_level"]} ppm</div></div>', unsafe_allow_html=True)

#             st.write("<br>", unsafe_allow_html=True)

#             # Spline Charts
#             ch1, ch2, ch3 = st.columns(3)
#             with ch1:
#                 st.subheader("Temperature Trend")
#                 st.plotly_chart(plot_spline_chart(display_df, 'temperature', '#ff6b6b', 'Temp'), use_container_width=True)
#             with ch2:
#                 st.subheader("Humidity Trend")
#                 st.plotly_chart(plot_spline_chart(display_df, 'humidity', '#339af0', 'Humidity'), use_container_width=True)
#             with ch3:
#                 st.subheader("Methane Gas Trend")
#                 st.plotly_chart(plot_spline_chart(display_df, 'gas_level', '#20c997', 'Methane'), use_container_width=True)
#     else:
#         st.info("Waiting for data from IoT Simulator... (Ensure Backend & Simulator are running)")

# # ==========================================
# # TAB 2: VEGGIE AI SCANNER
# # ==========================================
# with tab2:
#     st.header("🥕 Veggie AI Scanner & Freshness Predictor")
#     uploaded_file = st.file_uploader("Choose a produce image...", type=["jpg", "jpeg", "png"])
#     selected_shelf = st.selectbox("Assign Shelf", ["Shelf A1", "Shelf B2", "Shelf C3"])

#     if uploaded_file and st.button("🔍 Run AI Diagnostics"):
#         with st.spinner("Processing image via YOLOv8 and Q10 model..."):
#             try:
#                 files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
#                 data = {"shelf_id": selected_shelf}
#                 res = requests.post(f"{BACKEND_URL}/api/v1/scan-veggie", files=files, data=data).json()
#                 if res.get("success"):
#                     st.success(f"Item assigned to {res['shelf_assigned']}!")
#                     st.json(res["freshness_assessment"])
#                 else:
#                     st.warning(res.get("message", "No item detected."))
#             except Exception as e:
#                 st.error(f"Backend Connection Error: {e}")

# # ==========================================
# # TAB 3: INVENTORY
# # ==========================================
# with tab3:
#     st.header("📦 Warehouse Inventory")
#     try:
#         res = requests.get(f"{BACKEND_URL}/api/v1/inventory").json()
#         if res.get("success") and res.get("inventory"):
#             st.dataframe(pd.DataFrame(res["inventory"]), use_container_width=True)
#         else:
#             st.info("Inventory is currently empty.")
#     except Exception as e:
#         st.error(f"Failed to fetch inventory: {e}")

# # ==========================================
# # TAB 4: SYSTEM LOGS
# # ==========================================
# with tab4:
#     st.header("🛠️ Telemetry Logs")
#     df_logs = load_telemetry_data()
#     if not df_logs.empty:
#         st.dataframe(df_logs, use_container_width=True)

import os
import sqlite3
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(page_title="SMARTA Dashboard", page_icon="🌱", layout="wide")

# --- Global Configs ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DB_PATH = os.getenv("DB_PATH", "smarta.db")

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
        if not os.path.exists(DB_PATH):
            return pd.DataFrame()
        conn = sqlite3.connect(DB_PATH, timeout=5)
        df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY id DESC LIMIT 300", conn)
        conn.close()
        return df
    except Exception:
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
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', errors='coerce').dt.tz_localize(None)
        
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
    
    # Input Mode Selector: Camera or File Upload
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
                    
                    # Extract prediction details safely
                    freshness = res.get("freshness_assessment", {})
                    item_name = freshness.get("item", "Unknown Produce")
                    days_left = freshness.get("estimated_days_remaining", "N/A")
                    exp_date = freshness.get("estimated_expiration_date", "N/A")
                    risk_level = str(freshness.get("degradation_risk", "Low"))
                    opt_temp = freshness.get("optimal_temp_c", "N/A")

                    st.markdown("---")
                    st.subheader(f"🔍 AI Freshness Assessment Results")

                    # Row 1: KPI Summary Cards
                    c1, c2, c3 = st.columns(3)
                    c1.metric("📦 Detected Produce", item_name)
                    c2.metric("⏳ Est. Days Remaining", f"{days_left} Days")
                    c3.metric("📅 Expiration Date", exp_date)

                    st.write("<br>", unsafe_allow_html=True)
                    
                    # Row 2: Visual Risk Progress & Storage Advice
                    r_col1, r_col2 = st.columns([2, 1])

                    with r_col1:
                        st.write("**Microclimate Degradation Risk**")
                        if risk_level.lower() == "high":
                            st.error("⚠️ **HIGH DEGRADATION RISK** — Accelerated spoilage detected!")
                            st.progress(0.25)
                        elif risk_level.lower() == "medium":
                            st.warning("⚡ **MODERATE RISK** — Monitor microclimate conditions closely.")
                            st.progress(0.60)
                        else:
                            st.success("🟢 **LOW RISK / OPTIMAL** — Storage parameters are within nominal bounds.")
                            st.progress(0.95)

                    with r_col2:
                        st.info(f"❄️ **Target Temperature:** `{opt_temp}°C`")
                        
                else:
                    st.warning(res.get("message", "No item detected in image."))
            except Exception as e:
                st.error(f"Backend Connection Error: {e}")

# ==========================================
# TAB 3: INVENTORY
# ==========================================
with tab3:
    st.header("📦 Warehouse Inventory")
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
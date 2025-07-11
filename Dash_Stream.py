import streamlit as st
import requests
import time
import json
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Configuration
BLYNK_TOKEN = "eLlKTGdFtvexV_IyUx5AlTNku7Wl52zD"
BLYNK_BASE_URL = "https://blynk.cloud/external/api"
TEMPLATE_ID = "TMPL31O0n4AIQ"
TEMPLATE_NAME = "MotorControl"

# Page configuration
st.set_page_config(
    page_title="Motor Control Dashboard",
    page_icon="🚿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .motor-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        color: white;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    .status-on {
        color: #4ade80;
        font-weight: bold;
    }
    
    .status-off {
        color: #f87171;
        font-weight: bold;
    }
    
    .stButton > button {
        width: 100%;
        height: 60px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .sidebar .stSelectbox {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    h1, h2, h3 {
        color: white;
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'motor_state' not in st.session_state:
    st.session_state.motor_state = 0
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'total_runtime' not in st.session_state:
    st.session_state.total_runtime = 245
if 'current_runtime' not in st.session_state:
    st.session_state.current_runtime = 0

# API Functions
def set_motor_state(state: int):
    """Send motor state to Blynk API"""
    url = f"{BLYNK_BASE_URL}/update?token={BLYNK_TOKEN}&v1={state}"
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_motor_state():
    """Get motor state from Blynk API"""
    url = f"{BLYNK_BASE_URL}/get?token={BLYNK_TOKEN}&v1"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return int(response.text)
        return -1
    except requests.exceptions.RequestException:
        return -1

def get_sensor_data():
    """Simulate sensor data - replace with actual Blynk API calls"""
    import random
    return {
        'temperature': round(24.5 + random.uniform(-2, 2), 1),
        'humidity': round(68 + random.uniform(-5, 5), 1),
        'voltage': round(12.3 + random.uniform(-0.5, 0.5), 1),
        'current': round(2.1 + random.uniform(-0.3, 0.3), 1)
    }

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ Control Panel")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto Refresh", value=True)
    
    if auto_refresh:
        refresh_interval = st.slider("Refresh Interval (seconds)", 1, 30, 5)
        
    # Manual refresh button
    if st.button("🔄 Refresh Now"):
        st.rerun()
    
    st.markdown("---")
    
    # Device Information
    st.markdown("## 📱 Device Info")
    st.markdown(f"**Template ID:** `{TEMPLATE_ID}`")
    st.markdown(f"**Template Name:** `{TEMPLATE_NAME}`")
    st.markdown(f"**Device Type:** ESP32")
    st.markdown(f"**Firmware:** v1.0.0")
    
    st.markdown("---")
    
    # Connection Status
    st.markdown("## 🔗 Connection")
    connection_status = get_motor_state()
    if connection_status != -1:
        st.success("✅ Connected to Blynk")
    else:
        st.error("❌ Connection Failed")

# Main Dashboard
st.markdown("# 🚿 Motor Control Dashboard")
st.markdown("### Advanced IoT Motor Management System")

# Get current data
current_state = get_motor_state()
sensor_data = get_sensor_data()

if current_state != -1:
    st.session_state.motor_state = current_state
    st.session_state.last_update = datetime.now()

# Status Overview
col1, col2, col3, col4 = st.columns(4)

with col1:
    status_text = "🟢 RUNNING" if st.session_state.motor_state == 1 else "🔴 STOPPED"
    status_color = "normal" if st.session_state.motor_state == 1 else "inverse"
    st.metric("Motor Status", status_text)

with col2:
    st.metric("Temperature", f"{sensor_data['temperature']}°C", f"{sensor_data['temperature'] - 24.5:.1f}")

with col3:
    st.metric("Humidity", f"{sensor_data['humidity']}%", f"{sensor_data['humidity'] - 68:.1f}")

with col4:
    st.metric("Supply Voltage", f"{sensor_data['voltage']}V", f"{sensor_data['voltage'] - 12.3:.1f}")

st.markdown("---")

# Main Control Section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 🎮 Motor Control")
    
    # Control buttons
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        if st.button("🟢 START MOTOR", 
                    disabled=st.session_state.motor_state == 1,
                    type="primary"):
            with st.spinner("Starting motor..."):
                if set_motor_state(1):
                    st.session_state.motor_state = 1
                    st.success("✅ Motor started successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to start motor")
    
    with button_col2:
        if st.button("🔴 STOP MOTOR", 
                    disabled=st.session_state.motor_state == 0,
                    type="secondary"):
            with st.spinner("Stopping motor..."):
                if set_motor_state(0):
                    st.session_state.motor_state = 0
                    st.success("✅ Motor stopped successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to stop motor")
    
    # Current Status Display
    st.markdown("### Current Status")
    status_container = st.container()
    with status_container:
        if st.session_state.motor_state == 1:
            st.markdown('<div class="status-on">🟢 MOTOR IS RUNNING</div>', unsafe_allow_html=True)
            # Simulate runtime counter
            runtime_minutes = st.session_state.current_runtime // 60
            runtime_seconds = st.session_state.current_runtime % 60
            st.markdown(f"**Runtime:** {runtime_minutes:02d}:{runtime_seconds:02d}")
        else:
            st.markdown('<div class="status-off">🔴 MOTOR IS STOPPED</div>', unsafe_allow_html=True)
    
    st.markdown(f"**Last Update:** {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

with col2:
    st.markdown("## 📊 System Metrics")
    
    # Create a gauge chart for voltage
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = sensor_data['voltage'],
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Supply Voltage (V)"},
        delta = {'reference': 12.0},
        gauge = {
            'axis': {'range': [None, 15]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 10], 'color': "lightgray"},
                {'range': [10, 13], 'color': "gray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 14}}))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# Performance Analytics
st.markdown("---")
st.markdown("## 📈 Performance Analytics")

col1, col2 = st.columns(2)

with col1:
    # Runtime Chart
    runtime_data = pd.DataFrame({
        'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'Runtime (hrs)': [4.2, 3.8, 5.1, 4.7, 4.9, 3.2, 2.8]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=runtime_data['Day'],
        y=runtime_data['Runtime (hrs)'],
        name='Daily Runtime',
        marker_color='rgba(58, 71, 80, 0.6)'
    ))
    
    fig.update_layout(
        title="Weekly Runtime Analysis",
        xaxis_title="Day",
        yaxis_title="Runtime (hours)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Temperature & Humidity Chart
    hours = list(range(24))
    temp_data = [22 + 5 * abs(h - 12) / 12 for h in hours]
    humidity_data = [60 + 20 * abs(h - 12) / 12 for h in hours]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=hours, y=temp_data, name="Temperature (°C)", 
                  line=dict(color='red', width=3)),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=hours, y=humidity_data, name="Humidity (%)", 
                  line=dict(color='blue', width=3)),
        secondary_y=True,
    )
    
    fig.update_xaxes(title_text="Hour of Day")
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
    fig.update_yaxes(title_text="Humidity (%)", secondary_y=True)
    
    fig.update_layout(
        title="24-Hour Environmental Data",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# System Information
st.markdown("---")
st.markdown("## 🔧 System Information")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.markdown("### Hardware")
    st.markdown("- **MCU:** ESP32-WROOM-32")
    st.markdown("- **Relay:** 5V Single Channel")
    st.markdown("- **Motor:** 12V DC Pump")
    st.markdown("- **Sensors:** DHT22, Voltage Divider")

with info_col2:
    st.markdown("### Network")
    st.markdown("- **Platform:** Blynk IoT")
    st.markdown("- **Protocol:** HTTPS REST API")
    st.markdown("- **Update Rate:** 3 seconds")
    st.markdown("- **Connectivity:** WiFi 802.11n")

with info_col3:
    st.markdown("### Statistics")
    st.markdown(f"- **Total Runtime:** {st.session_state.total_runtime} minutes")
    st.markdown("- **Uptime:** 2 days 14 hours")
    st.markdown("- **API Calls:** 15,432")
    st.markdown("- **Success Rate:** 99.7%")

# Footer
st.markdown("---")
st.markdown("### 🚀 Motor Control Dashboard • Powered by Blynk IoT & ESP32")
st.markdown("*Built with Streamlit for advanced IoT motor management*")

# Auto-refresh functionality
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
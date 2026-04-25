import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from streamlit_autorefresh import st_autorefresh

# -------------------------------
# CONFIG
# -------------------------------
API_BASE_URL = "https://fraud-detection-api-u8hg.onrender.com"

st.set_page_config(page_title="Fraud Detection System", layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}

/* Metric Cards */
.metric-box {
    background: #ffffff;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

/* Sidebar Analyze Button ALWAYS BLUE */
section[data-testid="stSidebar"] .stButton > button {
    background-color:#2563eb;
    color:white;
    border:none;
    font-weight:600;
    border-radius:8px;
}

/* Toggle Button Base */
div.stButton > button {
    height: 45px;
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid #d1d5db;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("## 🛡 Fraud Detection System")
st.caption("Real-time transaction analysis powered by AI")

# ---------- SESSION STATE ----------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Prediction"

if "result" not in st.session_state:
    st.session_state.result = None

# ---------- TOGGLE HANDLERS ----------
def set_prediction():
    st.session_state.active_tab = "Prediction"

def set_insights():
    st.session_state.active_tab = "Insights"

# ---------- TOGGLE UI ----------
col1, col2 = st.columns(2, gap="small")

with col1:
    st.button("Prediction", on_click=set_prediction, use_container_width=True)

with col2:
    st.button("Insights", on_click=set_insights, use_container_width=True)


# Dynamic styling for toggle
if st.session_state.active_tab == "Prediction":
    pred_style = "background-color:#2563eb;color:white;border:none;"
    ins_style = "background-color:#f3f4f6;color:black;"
    exp_style = "background-color:#f3f4f6;color:black;"

elif st.session_state.active_tab == "Insights":
    pred_style = "background-color:#f3f4f6;color:black;"
    ins_style = "background-color:#2563eb;color:white;border:none;"
    exp_style = "background-color:#f3f4f6;color:black;"


st.markdown(f"""
<style>
div[data-testid="column"]:nth-of-type(1) div.stButton > button {{
    {pred_style}
}}
div[data-testid="column"]:nth-of-type(2) div.stButton > button {{
    {ins_style}
}}
</style>
""", unsafe_allow_html=True)
st.markdown("---")

# ---------- SIDEBAR ----------
st.sidebar.header("Transaction Analysis")

mode = st.sidebar.radio(
    "Select Mode",
    ["Manual Input", "Live Transactions"]
)

# -------------------------------
# MANUAL MODE
# -------------------------------
if mode == "Manual Input":
    amount = st.sidebar.number_input("Transaction Amount (INR)", 100, 100000, 25000)
    velocity = st.sidebar.number_input("Velocity (last 1 hour)", 0, 20, 7)
    distance = st.sidebar.number_input("Distance from Home (km)", 0, 2000, 450)

    if st.sidebar.button("Analyze Transaction"):
        data = {
            "transaction_amount": amount,
            "velocity_last_1h": velocity,
            "distance_from_home_km": distance
        }

        try:
            response = requests.post(f"{API_BASE_URL}/predict", json=data)
            st.session_state.result = response.json()
            st.session_state.latest_input = data
        except:
            st.error("❌ API Connection Failed")

# -------------------------------
# LIVE MODE
# -------------------------------
if mode == "Live Transactions":
    st_autorefresh(interval=5000, key="refresh")

    try:
        response = requests.get(f"{API_BASE_URL}/random-transaction")
        data = response.json()

        if "analysis" in data:
            st.session_state.result = data["analysis"]
            st.session_state.latest_input = data["input"]

    except:
        st.error("❌ API Connection Failed")

# -------------------------------
# DISPLAY RESULTS
# -------------------------------
if st.session_state.result:

    result = st.session_state.result
    prob = result.get('fraud_probability', 0)
    risk = result.get('risk_level', 'UNKNOWN')
    action = result.get('recommended_action', 'N/A')

    percent = int(prob * 100)

    # =============================
    # 🔴 PREDICTION TAB
    # =============================
    if st.session_state.active_tab == "Prediction":

        # GET AI NOTE
        ai_note = result.get("ai_investigation_note", "No explanation available")

        # FORMAT MESSAGE
        message = ai_note.replace(", ", ". ")

        # ALERT
        if risk == "HIGH":
            st.error("🚨 HIGH Risk Transaction")
        elif risk == "MEDIUM":
            st.warning("⚠️ Suspicious Transaction")
        else:
            st.success("✅ Safe Transaction")

        # METRICS
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<div class='metric-box'><h4>Fraud Probability</h4><h1>{percent}%</h1></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='metric-box'><h4>Risk Level</h4><h1>{risk}</h1></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='metric-box'><h4>Action</h4><h2>{action}</h2></div>", unsafe_allow_html=True)

        # AI EXPLANATION BOX
        st.markdown("### AI Investigation Insight")

        st.info(message)
        st.markdown("---")

        # GAUGE
        st.subheader("Fraud Risk Meter")

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=percent,
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 30], 'color': "green"},
                    {'range': [30, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "red"},
                ],
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

        # INPUT SUMMARY
        st.markdown("### Transaction Summary")

        input_data = st.session_state.latest_input

        colA, colB, colC = st.columns(3)
        colA.metric("Amount", f"₹{input_data.get('transaction_amount', 0)}")
        colB.metric("Velocity", f"{input_data.get('velocity_last_1h', 0)} txns/hr")
        colC.metric("Distance", f"{input_data.get('distance_from_home_km', 0)} km")

    # =============================
    # 🔵 INSIGHTS TAB
    # =============================
    else:
        st.subheader("📊 Fraud Analytics Dashboard")

        # DEMO DATA
        df = pd.DataFrame({
            "transaction_day_of_week": np.random.choice(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], 200),
            "transaction_amount_inr": np.random.randint(100, 50000, 200),
            "velocity_last_1h": np.random.randint(0, 20, 200),
            "is_fraud": np.random.choice([0,1], 200),
            "is_international": np.random.choice([0,1], 200)
        })

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        with col1:
            st.markdown("### Weekly Fraud Trends")
            weekly = df.groupby("transaction_day_of_week")["is_fraud"].sum().reset_index()
            fig1 = px.line(weekly, x="transaction_day_of_week", y="is_fraud", markers=True)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("### Amount vs Fraud")
            fig2 = px.box(df, x="is_fraud", y="transaction_amount_inr", color="is_fraud")
            st.plotly_chart(fig2, use_container_width=True)

        with col3:
            st.markdown("### Domestic vs International")
            intl = df.groupby("is_international")["is_fraud"].mean().reset_index()
            fig3 = px.bar(intl, x="is_international", y="is_fraud", color="is_international")
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown("### Velocity vs Amount")
            fig4 = px.scatter(df, x="velocity_last_1h", y="transaction_amount_inr", color="is_fraud")
            st.plotly_chart(fig4, use_container_width=True)
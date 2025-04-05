import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse

# Ensure user is logged in
if not st.session_state.get("logged_in"):
    st.switch_page("login.py")

# Ensure URL is selected
if "selected_url_id" not in st.session_state:
    st.warning("No URL selected.")
    st.stop()

BASE_URL = "http://localhost:3000"

url_id = st.session_state["selected_url_id"]
url_name = st.session_state.get("selected_url_name", "Selected URL")
st.title(f"Stats for: {url_name}")

# ---- FETCH CLICK DATA ----
def fetch_stats():
    try:
        res = requests.get(f"{BASE_URL}/url/stats/{url_id}")
        if res.status_code == 200:
            return res.json().get("clicks", [])
        else:
            st.error("Failed to fetch stats.")
    except Exception as e:
        st.error("Could not connect to backend.")
        st.text(str(e))
    return []

clicks = fetch_stats()

if not clicks:
    st.info("No click data yet.")
    st.stop()

# ---- PREPROCESSING ----
df = pd.DataFrame(clicks)

# Parse timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Extract domain from referrer
def get_domain(ref):
    try:
        return urlparse(ref).netloc or "direct"
    except:
        return "unknown"

df["referrer_domain"] = df["referrer"].apply(get_domain)

# Ensure location field exists and fill blanks
if "location" in df.columns:
    df["location"] = df["location"].fillna("Unknown")
else:
    df["location"] = "Unknown"

# ---- VISUALIZATION ----
st.subheader("Clicks Over Time")
time_series = df.groupby(df["timestamp"].dt.floor("H")).size().reset_index(name="clicks")
fig_time = px.line(time_series, x="timestamp", y="clicks", markers=True)
st.plotly_chart(fig_time, use_container_width=True)

st.subheader("Clicks by Location")
location_stats = df["location"].value_counts().reset_index()
location_stats.columns = ["Location", "Clicks"]
fig_location = px.bar(location_stats, x="Location", y="Clicks", color="Location")
st.plotly_chart(fig_location, use_container_width=True)

st.subheader("Clicks by Referrer")
ref_stats = df["referrer_domain"].value_counts().reset_index()
ref_stats.columns = ["Referrer", "Clicks"]
fig_ref = px.bar(ref_stats, x="Referrer", y="Clicks", color="Referrer")
st.plotly_chart(fig_ref, use_container_width=True)

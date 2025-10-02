import streamlit as st
from utils import fetch_videos

st.set_page_config(page_title="YouTube Dashboard", layout="wide")

st.title("📊 YouTube Analytics Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
limit = st.sidebar.slider("Number of videos to show", 5, 50, 20)

# Fetch data
df = fetch_videos(limit)

if df.empty:
    st.warning("No data available. Run the Airflow DAGs first.")
else:
    st.subheader("Latest Video Metrics")
    st.dataframe(df)

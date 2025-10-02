import os
import psycopg2
import pandas as pd
import streamlit as st

DB = dict(host=os.getenv("POSTGRES_HOST","localhost"), port=int(os.getenv("POSTGRES_PORT","5432")),
          dbname=os.getenv("POSTGRES_DB","postgres"), user=os.getenv("POSTGRES_USER","postgres"),
          password=os.getenv("POSTGRES_PASSWORD","postgres"))

@st.cache_data(ttl=300)
def load_top():
    with psycopg2.connect(**DB) as c:
        q = """
        SELECT v.video_id, v.title, max(f.view_count) as max_views
        FROM core.fact_video_metrics f
        JOIN core.dim_video v USING (video_id)
        GROUP BY v.video_id, v.title
        ORDER BY max_views DESC
        LIMIT 20;
        """
        return pd.read_sql(q, c)
df = load_top()
st.title("YouTube Analytics (MrBeast)")
st.dataframe(df)

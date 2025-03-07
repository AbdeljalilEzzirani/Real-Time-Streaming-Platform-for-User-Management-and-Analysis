import streamlit as st
from cassandra.cluster import Cluster
import pandas as pd

cluster = Cluster(['cassandra'])
session = cluster.connect('random_user_keyspace')

st.title("Real-Time User Analytics")

rows = session.execute("SELECT * FROM country_stats")
df = pd.DataFrame(rows)
st.bar_chart(df.set_index("country")[["user_count"]])

if st.button("Refresh"):
    st.experimental_rerun()
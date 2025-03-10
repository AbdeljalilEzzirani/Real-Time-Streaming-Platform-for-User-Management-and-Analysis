import streamlit as st
from pymongo import MongoClient
from cassandra.cluster import Cluster
import pandas as pd
import time

# MongoDB Connection
mongo_client = MongoClient("mongodb://mongodb:27017/")
mongo_db = mongo_client["randomUserDB"]
mongo_collection = mongo_db["randomUserCollection"]

# Cassandra Connection
cassandra_cluster = Cluster(['cassandra'])
cassandra_session = cassandra_cluster.connect("random_user_keyspace")

# Streamlit Dashboard
st.title("Real-Time User Data Dashboard")

# Tabs for MongoDB and Cassandra
tab1, tab2 = st.tabs(["Raw User Data (MongoDB)", "Aggregated Stats (Cassandra)"])

# MongoDB Raw Data
with tab1:
    st.header("Live User Data")
    placeholder_mongo = st.empty()  # Placeholder for live updates
    while True:
        # Fetch data from MongoDB
        mongo_data = list(mongo_collection.find().limit(50))  # Limit to last 50 records
        mongo_df = pd.DataFrame(mongo_data)
        if not mongo_df.empty:
            mongo_df = mongo_df.drop(columns=["_id"])  # Remove MongoDB _id field
            placeholder_mongo.dataframe(mongo_df)
        else:
            placeholder_mongo.write("No data available yet in MongoDB.")
        time.sleep(5)  # Refresh every 5 seconds

# Cassandra Aggregated Data
with tab2:
    st.header("Aggregated Country Stats")
    placeholder_cassandra = st.empty()  # Placeholder for live updates
    while True:
        # Fetch data from Cassandra
        rows = cassandra_session.execute("SELECT * FROM country_stats LIMIT 50")
        cassandra_data = [{"country": row.country, "window_start": row.window_start, 
                           "window_end": row.window_end, "avg_age": row.avg_age, 
                           "user_count": row.user_count} for row in rows]
        cassandra_df = pd.DataFrame(cassandra_data)
        if not cassandra_df.empty:
            placeholder_cassandra.dataframe(cassandra_df)
        else:
            placeholder_cassandra.write("No aggregated data available yet in Cassandra.")
        time.sleep(10)  # Refresh every 10 seconds

# Cleanup (won't reach here due to infinite loop, but good practice)
mongo_client.close()
cassandra_cluster.shutdown()

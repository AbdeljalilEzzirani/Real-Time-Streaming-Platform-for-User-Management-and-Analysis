from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, current_timestamp, from_json, window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
from pymongo import MongoClient

# Test MongoDB connection
client = MongoClient("mongodb://mongodb:27017/", serverSelectionTimeoutMS=5000)
try:
    client.admin.command("ping")
    print("MongoDB connection successful!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
finally:
    client.close()

spark = SparkSession.builder \
    .appName("UserStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0,org.mongodb:mongodb-driver-sync:4.11.0") \
    .config("spark.jars", "/opt/spark/jars/mongo-spark-connector_2.12-10.3.0.jar,/opt/spark/jars/guava-32.0.1-jre.jar,/opt/spark/jars/scala-library-2.12.18.jar") \
    .config("spark.mongodb.output.uri", "mongodb://mongodb:27017/randomUserDB.randomUserCollection") \
    .config("spark.mongodb.input.uri", "mongodb://mongodb:27017/randomUserDB.randomUserCollection") \
    .config("spark.mongodb.connection.uri", "mongodb://mongodb:27017/") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.hadoop.fs.defaultFS", "file:///") \
    .master("local[*]") \
    .getOrCreate()

# Print Spark config to debug
print("Spark MongoDB Config:")
print(spark.conf.get("spark.mongodb.output.uri"))
print(spark.conf.get("spark.mongodb.connection.uri"))

schema = StructType([
    StructField("results", ArrayType(StructType([
        StructField("name", StructType([
            StructField("first", StringType()),
            StructField("last", StringType())
        ])),
        StructField("location", StructType([
            StructField("country", StringType())
        ])),
        StructField("dob", StructType([
            StructField("age", IntegerType())
        ])),
        StructField("gender", StringType())
    ])))
])

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "random_user_data") \
    .option("startingOffsets", "earliest") \
    .load()

parsed_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select(explode("data.results").alias("user")) \
    .select(
        col("user.name.first").alias("first_name"),
        col("user.name.last").alias("last_name"),
        col("user.location.country").alias("country"),
        col("user.dob.age").alias("age"),
        col("user.gender").alias("gender"),
        current_timestamp().alias("ingestion_time")
    )

parsed_df_with_watermark = parsed_df.withWatermark("ingestion_time", "10 minutes")

mongo_query = parsed_df_with_watermark.writeStream \
    .format("mongodb") \
    .option("spark.mongodb.connection.uri", "mongodb://mongodb:27017/") \
    .option("spark.mongodb.output.uri", "mongodb://mongodb:27017/randomUserDB.randomUserCollection") \
    .option("uri", "mongodb://mongodb:27017/randomUserDB.randomUserCollection") \
    .option("database", "randomUserDB") \
    .option("collection", "randomUserCollection") \
    .option("checkpointLocation", "/tmp/checkpoint_mongo") \
    .option("forceDeleteTempCheckpointLocation", "true") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

agg_df = parsed_df_with_watermark.groupBy(
    col("country"),
    window(col("ingestion_time"), "10 minutes")
).agg(
    {"age": "avg", "*": "count"}
).withColumnRenamed("avg(age)", "avg_age") \
 .withColumnRenamed("count(1)", "user_count") \
 .select(
     col("country"),
     col("window.start").alias("window_start"),
     col("window.end").alias("window_end"),
     col("avg_age"),
     col("user_count")
 )

cassandra_query = agg_df.writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "random_user_keyspace") \
    .option("table", "country_stats") \
    .option("checkpointLocation", "/tmp/checkpoint_cassandra") \
    .outputMode("append") \
    .trigger(processingTime="10 seconds") \
    .start()

mongo_query.awaitTermination()
cassandra_query.awaitTermination()
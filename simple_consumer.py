from pyspark.sql import SparkSession
import logging
logger = logging.getLogger(__name__)

spark = SparkSession.builder \
    .appName("SparkStreamingExample") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
    .config("spark.hadoop.fs.defaultFS", "file:///") \
    .getOrCreate()

kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "random_user_data") \
    .option("startingOffsets", "earliest") \
    .load()

query = kafka_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("checkpointLocation", "/tmp/kafka-checkpoint") \
    .start()

query.awaitTermination()


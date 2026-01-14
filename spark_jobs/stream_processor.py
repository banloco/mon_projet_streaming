from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, timestamp_seconds
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

def write_to_influx(df, batch_id):
    # Configuration InfluxDB
    token = "my-super-secret-token"
    org = "myorg"
    bucket = "crypto"
    url = "http://influxdb:8086"

    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Conversion des lignes Spark en points InfluxDB
    for row in df.collect():
        point = Point("crypto_avg") \
            .tag("symbol", row['symbol']) \
            .field("average_price", float(row['average_price'])) \
            .time(row['window']['start'])
        write_api.write(bucket=bucket, org=org, record=point)

    client.close()

spark = SparkSession.builder.appName("CryptoAnalytics").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("symbol", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("time", LongType(), True)
])

# 1. Lecture
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:29092") \
    .option("subscribe", "crypto-prices") \
    .load()

# 2. Parsing et conversion avec ajout du Watermark
trades = raw_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", timestamp_seconds(col("time") / 1000)) \
    .withWatermark("timestamp", "1 minute")  # <--- AJOUTER CECI

# 3. AGRÉGATION
stats_df = trades.groupBy(
    window(col("timestamp"), "30 seconds"),
    col("symbol")
).agg({"price": "avg"}).withColumnRenamed("avg(price)", "average_price")

# 4. Double écriture
# Console pour voir si Spark reçoit bien de Kafka
query_console = stats_df.writeStream \
    .outputMode("update") \
    .format("console") \
    .trigger(processingTime='5 seconds') \
    .start()

# InfluxDB pour la persistance
query_influx = stats_df.writeStream \
    .foreachBatch(write_to_influx) \
    .outputMode("update") \
    .trigger(processingTime='5 seconds') \
    .start()

spark.streams.awaitAnyTermination()
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, unbase64, base64, split
from pyspark.sql.types import StructField, StructType, StringType, BooleanType, ArrayType, DateType, FloatType

# Define Variables
KAFKA_BROKERS_STRING = 'kafka:19092'
STEDI_RISK_TOPIC = 'stedi.risk-score.v0'
REDIS_SERVER_TOPIC = 'redis-server'
STEDI_EVENTS_TOPIC = 'stedi-events'

schemaEvent = StructType([
    StructField('customer', StringType()),
    StructField('score', FloatType()),
    StructField('riskDate', DateType())
])


# TO-DO: using the spark application object, read a streaming dataframe from the Kafka topic stedi-events as the source
# Be sure to specify the option that reads all the events from the topic including those that were published before you started the spark stream
spark = SparkSession.builder.appName('STEDI-evemts-app').getOrCreate()
spark.sparkContext.setLogLevel("WARN")

redisEventsRDf = spark\
    .readStream\
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS_STRING) \
    .option("subscribe", STEDI_EVENTS_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# TO-DO: cast the value column in the streaming dataframe as a STRING 
redisEventsDf = redisEventsRDf.selectExpr("cast(key as string) key", "cast(value as string) value")

# TO-DO: parse the JSON from the single column "value" with a json object in it, like this:
# +------------+
# | value      |
# +------------+
# |{"custom"...|
# +------------+
#
# and create separated fields like this:
# +------------+-----+-----------+
# |    customer|score| riskDate  |
# +------------+-----+-----------+
# |"sam@tes"...| -1.4| 2020-09...|
# +------------+-----+-----------+
#
# storing them in a temporary view called CustomerRisk

redisEventsDf.withColumn("value", from_json("value", schemaEvent))\
    .select(col("value.*"))\
    .createOrReplaceTempView("CustomerRisk")

# TO-DO: execute a sql statement against a temporary view, selecting the customer and the score from the temporary view, creating a dataframe called customerRiskStreamingDF
# TO-DO: sink the customerRiskStreamingDF dataframe to the console in append mode
# 
# It should output like this:
#
# +--------------------+-----
# |customer           |score|
# +--------------------+-----+
# |Spencer.Davis@tes...| 8.0|
# +--------------------+-----
# Run the python script by running the command from the terminal:
# /home/workspace/submit-event-kafka-streaming.sh
# Verify the data looks correct 

customerRiskStreamingDF = spark.sql("select customer, score from CustomerRisk")
customerRiskStreamingDF.writeStream.format("console").outputMode("append").start().awaitTermination()
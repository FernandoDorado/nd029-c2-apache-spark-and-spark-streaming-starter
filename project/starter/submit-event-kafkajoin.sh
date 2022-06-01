#!/bin/bash
docker exec -it spark /opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 sparkpykafkajoin.py | tee ../../spark/logs/kafkajoin.log 
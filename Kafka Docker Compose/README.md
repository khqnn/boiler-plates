
**Create an Event**
```bash
docker exec -it local-kafka /opt/kafka/bin/kafka-topics.sh --create --topic test-events --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092
```


**Open the Consumer**
```bash
docker exec -it local-kafka /opt/kafka/bin/kafka-console-consumer.sh --topic test-events --from-beginning --bootstrap-server 127.0.0.1:9092
```

**Open the Writer / Producer**
```bash
docker exec -it local-kafka /opt/kafka/bin/kafka-console-producer.sh --topic test-events --bootstrap-server 127.0.0.1:9092
```


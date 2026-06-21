import json
import os
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

_producer = None

def get_producer():
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(2, 0, 0)
            )
        except Exception as e:
            print(f"[Kafka Producer ERROR] Could not initialize: {e}")
            return None
    return _producer

def publish_event(topic, event_type, data):
    producer = get_producer()
    if producer:
        event = {
            'event_type': event_type,
            'data': data
        }
        try:
            producer.send(topic, event)
            producer.flush()
            print(f"[Kafka Event Published] Topic: {topic}, Type: {event_type}")
        except Exception as e:
            print(f"[Kafka Publish ERROR] Failed to send event: {e}")
    else:
        print(f"[Kafka Event Simulated] Topic: {topic}, Type: {event_type}, Data: {data}")

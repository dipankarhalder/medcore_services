import json
import os
import sys
import time
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

class Command(BaseCommand):
    help = 'Starts the Kafka consumer to process notifications'

    def handle(self, *args, **options):
        self.stdout.write("Starting Kafka Consumer...")
        
        consumer = None
        for i in range(15):
            try:
                consumer = KafkaConsumer(
                    'admin_auth_events',
                    'notification_events',
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    api_version=(2, 0, 0),
                    group_id='notification_group',
                    auto_offset_reset='earliest'
                )
                self.stdout.write(self.style.SUCCESS("Successfully connected to Kafka!"))
                break
            except Exception as e:
                self.stdout.write(f"Kafka connection attempt {i+1} failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)
                
        if not consumer:
            self.stdout.write(self.style.ERROR("Could not connect to Kafka. Exiting."))
            sys.exit(1)
            
        self.stdout.write("Waiting for events...")
        try:
            for message in consumer:
                event = message.value
                event_type = event.get('event_type')
                data = event.get('data', {})
                
                self.stdout.write(f"\n[RECEIVED EVENT] Topic: {message.topic}, Type: {event_type}")
                
                if event_type == 'user_registered':
                    username = data.get('username')
                    email = data.get('email')
                    self.stdout.write(self.style.SUCCESS(
                        f"==> Sending welcome email to {username} at {email}."
                    ))
                elif event_type == 'otp_generated':
                    otp_code = data.get('otp_code')
                    channel = data.get('channel')
                    target = data.get('target')
                    self.stdout.write(self.style.SUCCESS(
                        f"==> Sending Verification Code [{otp_code}] via {channel} to {target}."
                    ))
                else:
                    self.stdout.write(f"Unknown event type: {event_type}")
        except KeyboardInterrupt:
            self.stdout.write("Stopping Kafka Consumer...")
        finally:
            consumer.close()

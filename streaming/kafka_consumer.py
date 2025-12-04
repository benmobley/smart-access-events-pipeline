"""
Kafka Consumer - Ingests streaming data into PostgreSQL

Continuously reads events from Kafka topics and writes them to PostgreSQL
raw tables in near real-time.
"""

import json
import signal
import sys
from datetime import datetime
from typing import Dict, List
from kafka import KafkaConsumer
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import psycopg2

# Configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_GROUP_ID = 'smart-access-consumer-group'
DATABASE_URL = "postgresql://benmobley:@localhost:5432/smart_access"

TOPICS = {
    'access_events': 'smart-access.events',
    'device_health': 'smart-access.health'
}

# Batch settings for efficient writes
BATCH_SIZE = 100  # Commit every N messages
BATCH_TIMEOUT = 5  # Or every N seconds


class SmartAccessConsumer:
    """Consumes events from Kafka and writes to PostgreSQL."""
    
    def __init__(self):
        self.running = True
        self.engine = create_engine(DATABASE_URL, poolclass=NullPool)
        self.consumers = {}
        self.batches = {
            'access_events': [],
            'device_health': []
        }
        self.stats = {
            'access_events': 0,
            'device_health': 0
        }
        
        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals."""
        print("\n\n⏹️  Shutting down consumer...")
        self.running = False
    
    def _create_consumers(self):
        """Create Kafka consumers for each topic."""
        for topic_key, topic_name in TOPICS.items():
            consumer = KafkaConsumer(
                topic_name,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=KAFKA_GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',  # Start from latest for real-time
                enable_auto_commit=True,
                auto_commit_interval_ms=1000
            )
            self.consumers[topic_key] = consumer
            print(f"📡 Subscribed to topic: {topic_name}")
    
    def _batch_insert_events(self, events: List[Dict]):
        """Batch insert access events."""
        if not events:
            return
        
        with self.engine.begin() as conn:
            for event in events:
                # Map Kafka message to database schema
                db_event = {
                    'event_id': event['event_id'],
                    'device_id': event['device_id'],
                    'user_id': event.get('user_id', 1),  # Default user_id if not provided
                    'event_type': event['event_type'],
                    'trigger_source': event['trigger_source'],
                    'created_at': event['event_ts'],  # Map event_ts to created_at
                    'lat': event.get('lat', 0.0),  # Default lat/lon if not provided
                    'lon': event.get('lon', 0.0)
                }
                conn.execute(text("""
                    INSERT INTO raw_access_events 
                    (event_id, device_id, user_id, event_type, trigger_source, created_at, lat, lon)
                    VALUES (:event_id, :device_id, :user_id, :event_type, :trigger_source, :created_at, :lat, :lon)
                """), db_event)
        
        self.stats['access_events'] += len(events)
    
    def _batch_insert_health(self, health_reports: List[Dict]):
        """Batch insert device health reports."""
        if not health_reports:
            return
        
        with self.engine.begin() as conn:
            for report in health_reports:
                conn.execute(text("""
                    INSERT INTO raw_device_health 
                    (device_id, reported_at, battery_pct, signal_strength_dbm, is_online)
                    VALUES (:device_id, :reported_at, :battery_pct, :signal_strength_dbm, :is_online)
                """), report)
        
        self.stats['device_health'] += len(health_reports)
    
    def _process_batch(self, topic_key: str):
        """Process and insert a batch of messages."""
        batch = self.batches[topic_key]
        if not batch:
            return
        
        try:
            if topic_key == 'access_events':
                self._batch_insert_events(batch)
            elif topic_key == 'device_health':
                self._batch_insert_health(batch)
            
            # Clear batch after successful insert
            self.batches[topic_key] = []
            
            # Print stats every 500 messages
            total = sum(self.stats.values())
            if total % 500 == 0:
                print(f"✅ Consumed: {self.stats['access_events']} events, "
                      f"{self.stats['device_health']} health reports")
                
        except Exception as e:
            print(f"❌ Error inserting batch: {e}")
            # Keep batch for retry
    
    def consume(self):
        """Start consuming from all topics."""
        print("🚀 Starting Kafka consumer...")
        print(f"🔗 Database: {DATABASE_URL.split('@')[1]}")
        print(f"📊 Batch size: {BATCH_SIZE}, Timeout: {BATCH_TIMEOUT}s")
        print("\nConsuming... (Ctrl+C to stop)\n")
        
        self._create_consumers()
        
        import time
        last_commit_time = {key: time.time() for key in self.batches.keys()}
        
        try:
            while self.running:
                for topic_key, consumer in self.consumers.items():
                    # Poll for messages with short timeout
                    messages = consumer.poll(timeout_ms=100, max_records=BATCH_SIZE)
                    
                    for topic_partition, records in messages.items():
                        for record in records:
                            self.batches[topic_key].append(record.value)
                    
                    # Check if we should commit batch
                    current_time = time.time()
                    batch_size = len(self.batches[topic_key])
                    time_elapsed = current_time - last_commit_time[topic_key]
                    
                    if batch_size >= BATCH_SIZE or (batch_size > 0 and time_elapsed >= BATCH_TIMEOUT):
                        self._process_batch(topic_key)
                        last_commit_time[topic_key] = current_time
                
        except Exception as e:
            print(f"❌ Error in consumer loop: {e}")
        finally:
            # Process remaining batches
            print("\n📝 Processing remaining batches...")
            for topic_key in self.batches.keys():
                self._process_batch(topic_key)
            
            # Close consumers
            for consumer in self.consumers.values():
                consumer.close()
            
            print(f"\n📊 Final stats:")
            print(f"   Access events: {self.stats['access_events']}")
            print(f"   Health reports: {self.stats['device_health']}")
            print(f"   Total: {sum(self.stats.values())}")


if __name__ == '__main__':
    consumer = SmartAccessConsumer()
    consumer.consume()

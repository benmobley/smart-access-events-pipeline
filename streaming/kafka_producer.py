"""
Kafka Producer - Simulates real-time IoT device events

Generates smart access device events and streams them to Kafka topics
in real-time, simulating actual IoT device behavior with realistic timing.
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List
from kafka import KafkaProducer
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
TOPICS = {
    'access_events': 'smart-access.events',
    'device_health': 'smart-access.health'
}

# Simulation parameters
NUM_HOUSEHOLDS = 100  # Smaller for real-time demo
NUM_DEVICES_PER_HOUSEHOLD = 3
EVENT_RATE_PER_DEVICE = 0.1  # Events per second per device (1 every 10 sec)
HEALTH_CHECK_INTERVAL = 30  # Seconds between health reports

class SmartAccessProducer:
    """Streams synthetic smart access IoT events to Kafka."""
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        self.last_health_check = {}
        self.households = self._generate_households()
        self.devices = self._generate_devices()
        
    def _generate_households(self) -> List[Dict]:
        """Generate household data."""
        regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
        timezones = ['America/New_York', 'Europe/London', 'Asia/Tokyo', 'America/Sao_Paulo']
        
        households = []
        for i in range(1, NUM_HOUSEHOLDS + 1):
            region = random.choice(regions)
            households.append({
                'household_id': i,
                'name': fake.company(),
                'address': fake.address().replace('\n', ', '),
                'region': region,
                'timezone': random.choice(timezones),
                'created_at': fake.date_time_between(start_date='-2y', end_date='now').isoformat()
            })
        return households
    
    def _generate_devices(self) -> List[Dict]:
        """Generate device data."""
        device_types = ['garage_door', 'gate', 'smart_lock']
        models = {
            'garage_door': ['GD-2000', 'GD-3000', 'GD-Pro'],
            'gate': ['Gate-X1', 'Gate-X2', 'Gate-Master'],
            'smart_lock': ['Lock-S1', 'Lock-S2', 'Lock-Elite']
        }
        
        devices = []
        device_id = 1
        for household in self.households:
            for _ in range(NUM_DEVICES_PER_HOUSEHOLD):
                device_type = random.choice(device_types)
                devices.append({
                    'device_id': device_id,
                    'household_id': household['household_id'],
                    'device_type': device_type,
                    'model': random.choice(models[device_type]),
                    'firmware_version': f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 20)}",
                    'installed_at': fake.date_time_between(start_date='-1y', end_date='now').isoformat()
                })
                device_id += 1
                self.last_health_check[device_id - 1] = time.time()
        return devices
    
    def _generate_access_event(self, device: Dict) -> Dict:
        """Generate a single access event."""
        event_types = ['open', 'close', 'command_failed']
        event_weights = [45, 45, 10]  # 10% failure rate
        trigger_sources = ['app', 'button', 'remote', 'voice']
        
        return {
            'event_id': f"{device['device_id']}-{int(time.time() * 1000)}",
            'device_id': device['device_id'],
            'event_ts': datetime.utcnow().isoformat(),
            'event_type': random.choices(event_types, weights=event_weights)[0],
            'trigger_source': random.choice(trigger_sources)
        }
    
    def _generate_health_report(self, device: Dict) -> Dict:
        """Generate a device health report."""
        return {
            'device_id': device['device_id'],
            'reported_at': datetime.utcnow().isoformat(),
            'battery_pct': random.randint(20, 100),
            'signal_strength_dbm': random.randint(-90, -30),
            'is_online': random.choice([True, True, True, False])  # 75% online
        }
    
    def stream_events(self, duration_minutes: int = None):
        """
        Stream events to Kafka in real-time.
        
        Args:
            duration_minutes: How long to stream (None = infinite)
        """
        print(f"🚀 Starting Kafka producer...")
        print(f"📊 Households: {len(self.households)}, Devices: {len(self.devices)}")
        print(f"📈 Target rate: ~{len(self.devices) * EVENT_RATE_PER_DEVICE:.1f} events/sec")
        print(f"🔗 Topics: {list(TOPICS.values())}")
        print(f"⏱️  Duration: {'Infinite' if duration_minutes is None else f'{duration_minutes} minutes'}")
        print("\nStreaming... (Ctrl+C to stop)\n")
        
        start_time = time.time()
        event_count = 0
        health_count = 0
        
        try:
            while True:
                # Check duration
                if duration_minutes and (time.time() - start_time) > duration_minutes * 60:
                    break
                
                # Generate access events for random devices
                for device in self.devices:
                    if random.random() < EVENT_RATE_PER_DEVICE:
                        event = self._generate_access_event(device)
                        self.producer.send(
                            TOPICS['access_events'],
                            key=str(device['device_id']),
                            value=event
                        )
                        event_count += 1
                        
                        if event_count % 100 == 0:
                            print(f"✅ Sent {event_count} access events, {health_count} health reports")
                    
                    # Send health reports periodically
                    current_time = time.time()
                    if current_time - self.last_health_check[device['device_id']] >= HEALTH_CHECK_INTERVAL:
                        health = self._generate_health_report(device)
                        self.producer.send(
                            TOPICS['device_health'],
                            key=str(device['device_id']),
                            value=health
                        )
                        health_count += 1
                        self.last_health_check[device['device_id']] = current_time
                
                # Sleep to control rate
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping producer...")
        finally:
            self.producer.flush()
            self.producer.close()
            elapsed = time.time() - start_time
            print(f"\n📊 Summary:")
            print(f"   Total events: {event_count}")
            print(f"   Health reports: {health_count}")
            print(f"   Duration: {elapsed:.1f} seconds")
            print(f"   Rate: {event_count/elapsed:.2f} events/sec")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Stream smart access events to Kafka')
    parser.add_argument('--duration', type=int, help='Duration in minutes (default: infinite)')
    args = parser.parse_args()
    
    producer = SmartAccessProducer()
    producer.stream_events(duration_minutes=args.duration)

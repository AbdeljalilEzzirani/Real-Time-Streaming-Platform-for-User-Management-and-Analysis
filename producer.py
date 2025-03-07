import requests
import json
from kafka import KafkaProducer
import time

producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

while True:
    response = requests.get('https://randomuser.me/api/?results=10')
    data = response.json()
    producer.send('random_user_data', data)
    print("Sent batch of 10 users")
    time.sleep(10)
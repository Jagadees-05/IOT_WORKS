import json
import paho.mqtt.client as mqtt
import mysql.connector

# ---------- MQTT CONFIG ----------
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/ultrasonic"

# ---------- MYSQL CONFIG ----------
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
DATABASE_NAME = "IOT_WORKS"
TABLE_NAME = "ultrasonic"

# ---------- DATABASE SETUP ----------
def setup_database():
    db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )
    cursor = db.cursor()

    # Create database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
    cursor.execute(f"USE {DATABASE_NAME}")

    # Create table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            distance_cm FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.commit()
    cursor.close()
    db.close()
    print("Database and table ready ")

# ---------- INSERT DATA ----------
def insert_data(distance):
    db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DATABASE_NAME
    )
    cursor = db.cursor()
    sql = f"INSERT INTO {TABLE_NAME} (distance_cm) VALUES (%s)"
    cursor.execute(sql, (distance,))
    db.commit()
    cursor.close()
    db.close()

# ---------- MQTT CALLBACK ----------
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        distance = data["distance_cm"]

        print(f"Received Distance: {distance} cm")

        insert_data(distance)
        print("Stored in database \n")

    except Exception as e:
        print("Error:", e)

# ---------- MAIN ----------
setup_database()

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(MQTT_TOPIC)
client.on_message = on_message

print("MQTT Receiver Started... Waiting for data")
client.loop_forever()

import json
import mysql.connector
import paho.mqtt.client as mqtt

# ---------- MQTT CONFIG ----------
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/ldr"

# ---------- MYSQL CONFIG ----------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "iot_works"
TABLE_NAME = "ldr"

# ---------- DATABASE SETUP ----------
def setup_database():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            adc INT,
            state VARCHAR(10),
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# ---------- MQTT CALLBACKS ----------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT connected")
        client.subscribe(MQTT_TOPIC)
    else:
        print("MQTT connection failed")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print("Received:", payload)

    try:
        data = json.loads(payload)
        adc = data["adc"]
        state = data["state"]

        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        cursor.execute(
            f"INSERT INTO {TABLE_NAME} (adc, state) VALUES (%s, %s)",
            (adc, state)
        )

        conn.commit()
        cursor.close()
        conn.close()

        print("Inserted into database")

    except Exception as e:
        print("Error:", e)

# ---------- MAIN ----------
if __name__ == "__main__":
    setup_database()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

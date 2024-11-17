from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import pandas as pd

# devices range
device_st = 0
device_end = 5  # (0 to 4 for 5 devices)

# dataset path
data_path = "data/vehicle{}.csv"

# certs path
certificate_formatter = "output/certificate{}.pem.crt"
key_formatter = "output/private{}.pem.key"


class MQTTClient:
    def __init__(self, device_id, cert, key):
        """
        Initialize the MQTT client for a specific device.
        """
        self.device_id = f"veh{device_id}"
        self.client = AWSIoTMQTTClient(self.device_id)

        # Configure the MQTT client
        # TODO: add your url
        self.client.configureEndpoint(
            "a1wwi94zrbf34j-ats.iot.us-east-1.amazonaws.com", 8883
        )
        self.client.configureCredentials("AmazonRootCA1.pem", key, cert)
        self.client.configureOfflinePublishQueueing(-1)
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 seconds
        self.client.configureMQTTOperationTimeout(5)  # 5 seconds

        # Connect the client
        self.client.connect()

        # Subscribe to device results
        self.client.subscribe(f"iot/Vehicle_{self.device_id}", 1, self.customOnMessage)

    def customOnMessage(self, client, userdata, message):
        """
        Callback function to handle received messages  on the subscribed topic.
        """
        print(
            f"Device {self.device_id} received payload: {message.payload.decode('utf-8')} from topic: {message.topic}"
        )

    def customPubackCallback(self, mid):
        """
        Optional callback for publish acknowledgment (not used in this script).
        """
        pass

    def publish(self, topic="vehicle/emission/data"):
        """
        Publish vehicle emission data row by row to the specified topic.
        """
        # Load the vehicle's emission data
        df = pd.read_csv(data_path.format(self.device_id[-1]))
        for index, row in df.iterrows():
            # Add the vehicle_id to the row data
            data = row.to_dict()
            data["vehicle_id"] = self.device_id

            # Convert to JSON and publish to the topic
            payload = json.dumps(data)
            print(f"Publishing: {payload} to {topic}")
            self.client.publishAsync(
                topic, payload, 0, ackCallback=self.customPubackCallback
            )

            # sleep to simulate real-time
            time.sleep(1)


# Main program
print("Loading vehicle data...")
data = []
for i in range(device_st, device_end):
    print(f"- Reading data for device {i}")
    df = pd.read_csv(data_path.format(i))
    data.append(df)

print("Initializing MQTT clients...")
clients = []
for device_id in range(device_st, device_end):
    cert = certificate_formatter.format(device_id)
    key = key_formatter.format(device_id)
    client = MQTTClient(device_id, cert, key)
    clients.append(client)

# Handle user inputs for publishing data
while True:
    print("Press 's' to send data, 'd' to disconnect devices, or 'q' to quit:")
    x = input().lower()

    if x == "s":
        for client in clients:
            client.publish()
    elif x == "d":
        for client in clients:
            client.client.disconnect()
        print("All devices disconnected.")
        break
    elif x == "q":
        print("Exiting program.")
        break
    else:
        print("Invalid input. Try again.")
    time.sleep(3)

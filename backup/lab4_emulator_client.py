# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import pandas as pd
import numpy as np


#TODO 1: modify the following parameters
#Starting and end index, modify this
device_st = 0
device_end = 5
device_base = "Cama_CarDevice"

#Path to the dataset, modify this
data_path = "VehicleData/vehicle{}.csv"

#Path to your certificates, modify this
certificate_formatter = "VehicleCreds/certificate{}.pem.crt"
key_formatter = "VehicleCreds/private{}.pem.key"


class MQTTClient:
    def __init__(self, device_id, device_name, cert, key):
        # For certificate based connection
        self.device_id = str(device_id)
        self.device_name = str(device_name)
        self.state = 0
        self.client = AWSIoTMQTTClient(self.device_name)
        #TODO 2: modify your broker address
        self.client.configureEndpoint("ao7934fqx392l-ats.iot.us-east-2.amazonaws.com", 8883)
        # self.client.configureEndpoint("192.168.1.1", 8883)  # Use the IP address instead of the hostname
        self.client.configureCredentials("AmazonRootCA1.pem", key, cert)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        self.client.onMessage = self.customOnMessage
        

    def customOnMessage(self,message):
        #TODO 3: fill in the function to show your received message
        print("client {} received payload {} from topic {}".format(self.device_name, "stuff", "more stuff"))


    # Suback callback
    def customSubackCallback(self,mid, data):
        #You don't need to write anything here
        pass


    # Puback callback
    def customPubackCallback(self,mid):
        #You don't need to write anything here
        pass


    def publish(self, topic="vehicle/emission/data"):
    # Load the vehicle's emission data
        try:
            df = pd.read_csv(data_path.format(self.device_id))
            for index, row in df.iterrows():
                # Create a JSON payload from the row data
                payload = json.dumps(row.to_dict())

                # Publish the payload to the specified topic
                print(f"Publishing: {payload} to {topic}")
                self.client.publishAsync(topic, payload, 0, ackCallback=self.customPubackCallback)

                # Sleep to simulate real-time data publishing
                time.sleep(1)

        except Exception as e:
            print(f"Error during publishing: {e}")
            

print("Loading vehicle data...")
data = []
for i in range(5):
    a = pd.read_csv(data_path.format(i))
    data.append(a)

print("Initializing MQTTClients...")
clients = []
for device_id in range(device_st, device_end):
    device_name = f"{device_base}{device_id}"
    certificate = certificate_formatter.format(device_id)
    key = key_formatter.format(device_id)
    client = MQTTClient(device_id, device_name, certificate, key)
    try:
        client.client.connect()
        print(f"Device {device_id} connected successfully.")
    except Exception as e:
        print(f"Failed to connect device {device_id}: {e}")
    clients.append(client)
 

while True:
    print("send now?")
    x = input()
    if x == "s":
        for i,c in enumerate(clients):
            c.publish()

    elif x == "d":
        for c in clients:
            c.client.disconnect()
        print("All devices disconnected")
        exit()
    else:
        print("wrong key pressed")

    time.sleep(3)






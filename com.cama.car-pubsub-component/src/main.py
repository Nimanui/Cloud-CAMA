import sys
import json
import time
import logging
from awsiot.greengrasscoreipc import connect
from awsiot.greengrasscoreipc.model import (
    SubscribeToIoTCoreRequest,
    SubscriptionResponseMessage,
    QOS,
    PublishToIoTCoreRequest,
    UnauthorizedError,
)

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyAwsGreengrassV2Component:
    def __init__(self):
        self.ipc_client = connect()
        self.topic = "vehicle/emission/data"
        self.subscribe_to_topic(self.topic)

        # track max CO2 per vehicle
        self.max_co2_per_vehicle = {}

    def subscribe_to_topic(self, topic):
        request = SubscribeToIoTCoreRequest()
        request.topic_name = topic
        request.qos = QOS.AT_LEAST_ONCE

        try:
            handler = StreamHandler(self.process_message)
            operation = self.ipc_client.new_subscribe_to_iot_core(handler)
            future = operation.activate(request)
            future.result(10)  # Timeout after 10 seconds
            logger.info(f"Successfully subscribed to topic: {topic}")
        except UnauthorizedError:
            logger.error("Unauthorized error while subscribing to topic")
        except Exception as e:
            logger.error(f"Exception while subscribing to topic: {e}")

    def process_message(self, topic, payload):
        logger.info(f"Received message on {topic}: {payload}")

        try:
            message_payload = json.loads(payload.decode("utf-8"))
            # message_payload
            vehicle_id = message_payload.get("vehicle_id")
            co2_val = float(message_payload.get("vehicle_CO2"))

            # Update max CO2 for this vehicle
            current_max = self.max_co2_per_vehicle.get(vehicle_id, 0)
            if co2_val > current_max:
                self.max_co2_per_vehicle[vehicle_id] = co2_val
                # Publish to the device
                result_message = {"vehicle_id": vehicle_id, "max_CO2": co2_val}
                publish_topic = f"iot/Vehicle_{vehicle_id}"
                self.publish_message(result_message, topic=publish_topic)
                logger.info(
                    f"Published max CO2 {co2_val} for vehicle {vehicle_id} to topic {publish_topic}"
                )

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def publish_message(self, message, topic):
        request = PublishToIoTCoreRequest()
        request.topic_name = topic
        request.payload = bytes(json.dumps(message), "utf-8")
        request.qos = QOS.AT_LEAST_ONCE

        try:
            operation = self.ipc_client.new_publish_to_iot_core()
            future = operation.activate(request)
            future.result(10)  # Timeout after 10 seconds
            logger.info(f"Successfully published message to topic: {topic}")
        except UnauthorizedError:
            logger.error("Unauthorized error while publishing message")
        except Exception as e:
            logger.error(f"Exception while publishing message: {e}")


class StreamHandler:
    def __init__(self, process_message_callback):
        self.process_message_callback = process_message_callback

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        message = event.message
        payload = message.payload
        topic = message.topic_name
        self.process_message_callback(topic, payload)

    def on_stream_error(self, error: Exception) -> bool:
        logger.error(f"Received a stream error: {error}")
        return False  # Return True to keep the stream open, False to close it

    def on_stream_closed(self) -> None:
        logger.info("Stream was closed")


if __name__ == "__main__":
    # run
    component = MyAwsGreengrassV2Component()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

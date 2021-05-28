import boto3
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
from uuid import uuid4

TOPIC="hw4_iot"
message_to_mqtt="hello I'm toS3.py"
message_count=1
client_id="hw4-" + str(uuid4())
endpoint="a3dy894pqcozk5-ats.iot.us-east-1.amazonaws.com"

received_all_event = threading.Event()

received_count = 0
return_message='no message'


def send2S3():
    try:
    # TODO: write code...
        bucketname = "hw4-109062530"
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        isbucketExist=False
        # Output the bucket names
        for bucket in response['Buckets']:
            if bucket["Name"] == bucketname:
                isbucketExist=True
                print('Existing buckets')

        if isbucketExist==False:
            print('creat buckets')
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucketname)

        res=s3.upload_file("./test.jpg",bucketname ,"test.jpg",ExtraArgs={'ACL':'public-read', 'ContentType': 'image/jpeg'})
        return res
    except Exception as e:
        print(e)



# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
        resubscribe_results = resubscribe_future.result()
        print("Resubscribe results: {}".format(resubscribe_results))

        for topic, qos in resubscribe_results['topics']:
            if qos is None:
                sys.exit("Server rejected resubscribe to topic: {}".format(topic))



# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_count,return_message
    received_count += 1
    if received_count == message_count:
        return_message=payload
        received_all_event.set()


def waitforqueue():
    # Spin up resources

    io.init_logging(getattr(io.LogLevel, io.LogLevel.NoLogs.name), 'stderr')
    global received_count
    received_all_event.clear()
    received_count = 0
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    proxy_options = None
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath="/home/pi/certs/f1bfe03229-certificate.pem.crt",
        pri_key_filepath="/home/pi/certs/f1bfe03229-private.pem.key",
        client_bootstrap=client_bootstrap,
        ca_filepath="/home/pi/certs/AmazonRootCA1.pem",
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=client_id,
        clean_session=False,
        keep_alive_secs=6,
        http_proxy_options=proxy_options)

    print("Connecting to {} with client ID '{}'...".format(
        endpoint, client_id))
    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(TOPIC))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=TOPIC,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if message_count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")
    return return_message

if __name__ == "__main__":
    #send2S3()
    waitforqueue()

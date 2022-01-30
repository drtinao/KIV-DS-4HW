from kazoo.client import KazooClient
from paho.mqtt.client import Client
import lorem

import time
import sys
import logging
import socket  # for working with network con

# constants - START
PARENT_NODE_MQTT_BROKER = "mqtt_brokers_list"
NODE_NAME_MQTT_BROKER = "mqtt_node"
PARENT_NODE_MQTT_CLIENT = "mqtt_clients_list"
NODE_NAME_MQTT_CLIENT = "mqtt_client"
TIMEOUT_CON_ZOOKEEPER = 100000  # timeout within which connection to zookeeper should be established, seconds
MESSAGE_EVERY_SEC = 5
ONLINE_BROKERS_WAIT_SEC = 15
# constants - END

global kazooClient  # instance of kazoo, zookeeper
global mqtt_connected  # False when disconnected from broker, else True
global ephemeral_node_name  # name of ephemeral node created in mqtt_clients_list - represents client

# Returns hostname of the current machine.
def get_node_hostname():
    try:
        node_hostname = socket.gethostname()
        return node_hostname
    except:
        print("Error while getting node hostname")
        sys.stdout.flush()


# Returns IP of the current machine.
# node_hostname - hostname of the machine
def get_node_ip(node_hostname):
    try:
        node_ip = socket.gethostbyname(node_hostname)
        return node_ip
    except:
        print("Error while getting node IP")
        sys.stdout.flush()


# Returns available brokers list in PARENT_NODE_MQTT_BROKER.
# kazooClient - instance of Kazoo
def retrieve_online_brokers(kazooClient):
    mqtt_brokers_list = {}

    if kazooClient.exists('/' + PARENT_NODE_MQTT_BROKER):
        mqtt_brokers_list = kazooClient.get_children('/' + PARENT_NODE_MQTT_BROKER)
        print("Retrieved online brokers: " + str(mqtt_brokers_list))
        sys.stdout.flush()
        if mqtt_brokers_list and mqtt_brokers_list is not None:
            return mqtt_brokers_list

    if not mqtt_brokers_list or mqtt_brokers_list is None:
        print("Waiting for brokers... No entry in zookeeper yet.")
        sys.stdout.flush()
        time.sleep(ONLINE_BROKERS_WAIT_SEC)
        retrieve_online_brokers(kazooClient)

# Returns connected clients present in PARENT_NODE_MQTT_CLIENT.
# kazooClient - instance of Kazoo
def retrieve_online_clients(kazooClient):
    mqtt_clients_list = {}

    if kazooClient.exists('/' + PARENT_NODE_MQTT_CLIENT):
        mqtt_clients_list = kazooClient.get_children('/' + PARENT_NODE_MQTT_CLIENT)
        print("Retrieved online clients: " + str(mqtt_clients_list))
        sys.stdout.flush()

    return mqtt_clients_list

# Returns name of broker which is least occupied. Ie. minimum connections in PARENT_NODE_MQTT_CLIENT.
# mqtt_clients_list - ephemeral nodes present in PARENT_NODE_MQTT_CLIENT.
# mqtt_brokers_list - ephemeral nodes present in PARENT_NODE_MQTT_BROKER
def retrieve_least_occ_broker(mqtt_clients_list, mqtt_brokers_list):
    brokers_dict = {}  # key = number of broker, value = number of con clients

    # go through mqtt_brokers_list and retrieve num of each broker, create dict entry for each broker - START
    for mqtt_broker in mqtt_brokers_list:
        splitted_name = mqtt_broker.split(NODE_NAME_MQTT_BROKER)
        num_of_broker = splitted_name[1].lstrip('0')
        if not num_of_broker:
            num_of_broker = '0'
        brokers_dict[num_of_broker] = 0  # 0 client con at beginning
    # go through mqtt_brokers_list and retrieve num of each broker, create dict entry for each broker - END

    # go through mqtt_clients_list and retrieve num of broker to which is each client connected - START
    for connected_client in mqtt_clients_list:
        splitted_name = connected_client.split(NODE_NAME_MQTT_CLIENT)
        num_of_broker = splitted_name[0]
        brokers_dict[num_of_broker] = brokers_dict[num_of_broker] + 1  # increment server load in dict
    # go through mqtt_clients_list and retrieve num of broker to which is each client connected - END

    target_broker_num = min(brokers_dict.items(), key=lambda x: x[1])[0]
    return target_broker_num


# Returns number of broker to which client should connect to.
# kazooClient - instance of Kazoo
def find_target_broker(kazooClient):
    mqtt_brokers_list = retrieve_online_brokers(kazooClient)
    while not mqtt_brokers_list or mqtt_brokers_list is None or len(mqtt_brokers_list) == 0:
        mqtt_brokers_list = retrieve_online_brokers(kazooClient)

    mqtt_clients_list = retrieve_online_clients(kazooClient)

    if not mqtt_clients_list:  # no clients connected => pick any broker
        print("No clients yet => trying to connect to FIRST broker in list, num: " + mqtt_brokers_list[0])
        sys.stdout.flush()
        return add_padding_zoonode(mqtt_brokers_list[0])
    else:  # clients connected, get least occupied broker
        target_broker_num = retrieve_least_occ_broker(mqtt_clients_list, mqtt_brokers_list)
        print("Clients found => trying to connect to LEAST OCCUPIED broker, num: " + target_broker_num[0])
        sys.stdout.flush()
        return add_padding_zoonode(target_broker_num)

# Add padding to node to fit zookeeper convention (10 length).
# node_num - number of node (no padding)
def add_padding_zoonode(node_num):
    node_num_padded = str(node_num)

    if NODE_NAME_MQTT_BROKER in node_num_padded:
        node_num_padded = node_num_padded.replace(NODE_NAME_MQTT_BROKER, '')

    while len(node_num_padded) < 10:
        node_num_padded = "0" + node_num_padded

    node_num_padded = NODE_NAME_MQTT_BROKER + node_num_padded

    return node_num_padded

# Callback when message is received (MQTT).
def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + ": " + str(msg.payload))
    sys.stdout.flush()

# Callback when connected (MQTT).
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        print("Connected to MQTT broker!")
        sys.stdout.flush()
        create_mqtt_client_entry(userdata['target_broker_num'])
    else:
        mqtt_connected = False
        print("Failed to connect to MQTT broker, return code %d\n", rc)
        sys.stdout.flush()

# Callback when connection lost (MQTT).
def on_disconnect(client, userdata, rc):
    global mqtt_connected, ephemeral_node_name

    mqtt_connected = False
    client.loop_stop()
    print("MQTT broker disconnected! Waiting 20 seconds before electing another one...")
    sys.stdout.flush()
    if kazooClient.exists(ephemeral_node_name):
        sys.stdout.flush()
        kazooClient.delete(ephemeral_node_name)
    time.sleep(20)
    start_mqtt_process()

# Creates ephemeral + sequential node under PARENT_NODE_MQTT_CLIENT which represents online MQTT client.
# broker_num - number broker to which client is connected
def create_mqtt_client_entry(broker_num):
    global ephemeral_node_name

    ephemeral_node_name = kazooClient.create(path=PARENT_NODE_MQTT_CLIENT + '/' + str(broker_num) + NODE_NAME_MQTT_CLIENT, ephemeral=True, sequence=True)
    print("CLIENT CREATED EPHEMERAL ZOOKEEPER NODE: " + PARENT_NODE_MQTT_CLIENT + "/" + str(broker_num) + NODE_NAME_MQTT_CLIENT)
    sys.stdout.flush()

# Establishes connection to broker.
# broker_ip - IP of target broker to which connection should be established
# broker_num - number of broker in zookeeper list
def connect_to_broker(broker_ip, broker_num):
    print("Connecting to broker num: " + broker_num + ", IP: " + broker_ip)
    sys.stdout.flush()

    client = Client(userdata={'target_broker_num':broker_num})
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    sys.stdout.flush()
    client.connect(broker_ip, 1880, 60)
    return client

# Performs MQTT broker selection, then inits other steps - like connecting atc.
def start_mqtt_process():
    global mqtt_connected

    mqtt_connected = False
    broker_node_name = find_target_broker(kazooClient)
    target_broker_ip = kazooClient.get('/' + PARENT_NODE_MQTT_BROKER + '/' + broker_node_name)
    client = connect_to_broker(target_broker_ip[0], broker_node_name[-1])
    client.loop_start()
    client.subscribe("#")
    send_random_message(client, get_node_hostname())

# Sends random message using given mqtt client.
# mqtt_client - mqtt client instance
# topic - topic to which message should be published
def send_random_message(mqtt_client, topic):
    global mqtt_connected

    while True:
        if mqtt_connected:
            s = lorem.sentence()
            mqtt_client.publish(topic, s)
            print("Published message:" + s)
            sys.stdout.flush()
        time.sleep(MESSAGE_EVERY_SEC)
        send_random_message(mqtt_client, topic)

# connect to zookeeper server - START
logging.basicConfig()
zookeeper_servers = ['10.0.1.101:2181', '10.0.1.102:2181',
                     '10.0.1.103:2181']  # IPs + ports of available zookeeper servers
kazooClient = KazooClient(hosts=zookeeper_servers)
kazooClient.start(timeout=TIMEOUT_CON_ZOOKEEPER)
# connect to zookeeper server - END

start_mqtt_process()
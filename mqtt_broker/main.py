from kazoo.client import KazooClient
import time
import sys
import logging
import socket  # for working with network con
import subprocess

# constants - START
PARENT_NODE = "mqtt_brokers_list"
NODE_NAME = "mqtt_node"
PARENT_NODE_MQTT_CLIENT = "mqtt_clients_list"
TIMEOUT_CON_ZOOKEEPER = 100000  # timeout within which connection to zookeeper should be established, seconds
# constants - END

# Returns hostname of the current machine.
def get_node_hostname():
    try:
        node_hostname = socket.gethostname()
        return node_hostname
    except:
        print('Error while getting node hostname')
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

# connect to zookeeper server - START
logging.basicConfig()
zookeeper_servers = ['10.0.1.101:2181', '10.0.1.102:2181', '10.0.1.103:2181']  # IPs + ports of available zookeeper servers
kazooClient = KazooClient(hosts=zookeeper_servers)
kazooClient.start(timeout=TIMEOUT_CON_ZOOKEEPER)
# connect to zookeeper server - END

# create root node with brokers if not yet present - START
if not kazooClient.exists(PARENT_NODE):
    kazooClient.create(PARENT_NODE, ephemeral=False, sequence=False)
    print("BROKER CREATED PARENT ZOOKEEPER NODE WITH NAME: " + str(PARENT_NODE))
    sys.stdout.flush()
# create root node with brokers if not yet present - END

# create root node with clients if not yet present - START
if not kazooClient.exists(PARENT_NODE_MQTT_CLIENT):
    kazooClient.create(PARENT_NODE_MQTT_CLIENT, ephemeral=False, sequence=False)
    print("BROKER CREATED PARENT ZOOKEEPER NODE WITH NAME: " + str(PARENT_NODE_MQTT_CLIENT))
    sys.stdout.flush()
# create root node with clients if not yet present - END

# create children node for the broker with IP values
kazooClient.create(path=PARENT_NODE + '/' + NODE_NAME, value=get_node_ip(get_node_hostname()), ephemeral=True, sequence=True)
print("BROKER CREATED EPHEMERAL ZOOKEEPER NODE: " + str(PARENT_NODE) + str('/') + str(NODE_NAME))

# keep process up to let zookeeper know...
while True:
    p = subprocess.Popen(["/bin/bash", "-c", "pgrep mosquitto"], stdout=subprocess.PIPE)
    result = p.communicate()[0]
    if len(result) == 0:  # exit if mosquitto is down...
        exit()
    time.sleep(5)
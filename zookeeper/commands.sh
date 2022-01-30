#!/bin/bash

hostname | rev | cut -c '1-1' > /madagaskar/zookeeper/myid
/usr/local/zookeeper/bin/zkServer.sh start-foreground

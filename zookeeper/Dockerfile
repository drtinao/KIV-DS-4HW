#
# Use base image, install Apache ZooKeeper
#

FROM ghcr.io/maxotta/kiv-ds-docker:latest
COPY commands.sh /
RUN chmod u+x ./commands.sh
#RUN yum -q -y install python3

# install zookeeper - START
# install wget needed for zookeeper obtain
RUN yum -q -y install wget
# download zookeeper
RUN wget https://dlcdn.apache.org/zookeeper/zookeeper-3.7.0/apache-zookeeper-3.7.0-bin.tar.gz --no-check-certificate
# unpack zookeeper
RUN tar -zxf apache-zookeeper-3.7.0-bin.tar.gz
# move zookeeper install to local
RUN mv apache-zookeeper-3.7.0-bin /usr/local
# create link
RUN ln -s /usr/local/apache-zookeeper-3.7.0-bin/ /usr/local/zookeeper
# add path to Terminal
RUN echo export PATH=\"\$PATH:/usr/local/zookeeper/bin\" >> ~/.bashrc
# reload Terminal vars
RUN source ~/.bashrc
# install zookeeper - END

# configure zookeeper persistent data directory - START
RUN sudo mkdir -p /madagaskar/zookeeper
# configure zookeeper persistent data directory - END

# create zookeeper config file - START
# specify interval between heartbeats (shorter -> bigger overhead)
RUN echo "tickTime=2000" >> /usr/local/zookeeper/conf/zoo.cfg
# specify folder for persistent data storage (must exist!)
RUN echo "dataDir=/madagaskar/zookeeper" >> /usr/local/zookeeper/conf/zoo.cfg
# specify client port
RUN echo "clientPort=2181" >> /usr/local/zookeeper/conf/zoo.cfg
# specify max connected clients
RUN echo "maxClientCnxns=60" >> /usr/local/zookeeper/conf/zoo.cfg
# specify initial synchronization phase limit
RUN echo "initLimit=10" >> /usr/local/zookeeper/conf/zoo.cfg
# specify max time between sending a request / receiving ACK
RUN echo "syncLimit=5" >> /usr/local/zookeeper/conf/zoo.cfg
# setup zookeeper nodes - fixed, 3 total
RUN echo "server.1=10.0.1.101:2888:3888" >> /usr/local/zookeeper/conf/zoo.cfg
RUN echo "server.2=10.0.1.102:2888:3888" >> /usr/local/zookeeper/conf/zoo.cfg
RUN echo "server.3=10.0.1.103:2888:3888" >> /usr/local/zookeeper/conf/zoo.cfg
# create zookeeper config file - END

# specify node id - by hostname, each ends 1,2,3
# "hostname | rev | cut -c '1-1' > /madagaskar/zookeeper/myid" - PROVIDED BY VAGRANTFILE!

# install openjdk
RUN yum -q -y install java-1.8.0-openjdk

HEALTHCHECK --interval=5s CMD /usr/local/zookeeper/bin/zkServer.sh status | grep "Mode:" || exit 1

VAGRANTFILE_API_VERSION = "2"
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker' # docker is provider
ENV['FORWARD_DOCKER_PORTS'] = "1" # enable port forwarding

unless Vagrant.has_plugin?("vagrant-docker-compose")
  system("vagrant plugin install vagrant-docker-compose")
  puts "Dependencies installed, please try the command again."
  exit
end

ZOOKEEPER_IMAGE = "./zookeeper" # zookeeper app image
MQTT_BROKER_IMAGE = "./mqtt_broker" # mqtt broker image
MQTT_CLIENT_IMAGE = "./mqtt_client"  # mqtt client image

BASE_IMAGE  = "./nodes" # use base centos image, install with python
 
NODES = {:nameprefix => "zoonode-",  # prefix for node namesd.image = NODES[:image]
              :subnet => "10.0.1.", # basically IP prefix
              :ip_offset => 100,  # nodes will have IPs like: 10.0.1.101, .102
              :image => BASE_IMAGE, # use base centos img
              :port => 5000 } # port to use

MQTT_BROKER_NODES = {:nameprefix => "mqtt-broker-node-",  # prefix for node namesd.image = NODES[:image]
              :subnet => "10.0.1.", # basically IP prefix
              :ip_offset => 150,  # nodes will have IPs like: 10.0.1.151, .152
              :image => BASE_IMAGE, # use base centos img
              :port => 5000 } # port to use

MQTT_CLIENT_NODES = {:nameprefix => "mqtt-client-node-",  # prefix for node namesd.image = NODES[:image]
              :subnet => "10.0.1.", # basically IP prefix
              :ip_offset => 180,  # nodes will have IPs like: 10.0.1.181, .182
              :image => BASE_IMAGE, # use base centos img
              :port => 5000 } # port to use

ZOOKEEPER_COUNT = 3 # num of zookeeper instances
MQTT_BROKER_COUNT = 3 # num of mqtt broker instances
MQTT_CLIENT_COUNT = 5 # num of mqtt client instances

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config| # zookeeper node config start
  config.ssh.insert_key = false

  (1..ZOOKEEPER_COUNT).each do |i| # create 1 to N zookeeper nodes
    node_ip_addr = "#{NODES[:subnet]}#{NODES[:ip_offset] + i}"
    node_name = "#{NODES[:nameprefix]}#{i}"
    config.vm.define node_name do |s| # define one particular node
      s.vm.network "private_network", ip: node_ip_addr
      s.vm.hostname = node_name
      s.vm.provider "docker" do |d|
        d.build_dir = "./zookeeper"
        d.name = node_name
        d.has_ssh = true
      end
    end
  end

  config.vm.provision :shell, :run => 'always', :inline => "/commands.sh"
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config| # mqtt broker config start
  config.ssh.insert_key = false

  (1..MQTT_BROKER_COUNT).each do |i| # create 1 to N mosquitto mqtt brokes nodes
    node_ip_addr = "#{MQTT_BROKER_NODES[:subnet]}#{MQTT_BROKER_NODES[:ip_offset] + i}"
    node_name = "#{MQTT_BROKER_NODES[:nameprefix]}#{i}"
    config.vm.define node_name do |s| # define one particular node
      s.vm.network "private_network", ip: node_ip_addr
      s.vm.hostname = node_name
      s.vm.provider "docker" do |d|
        d.build_dir = "./mqtt_broker"
        if i != MQTT_BROKER_COUNT
            d.build_args = ["--build-arg", "BRIDGENAME=connection bridge-#{i}", "--build-arg", "BRIDGEADDRESS=address #{MQTT_BROKER_NODES[:subnet]}#{MQTT_BROKER_NODES[:ip_offset] + i + 1}:1880", "--build-arg", "TOPICOUT=topic # out 0", "--build-arg", "TOPICIN=topic # in 0"]
        end
        d.name = node_name
        d.has_ssh = true
      end
    end
  end
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config| # mqtt client config start
  config.ssh.insert_key = false

  (1..MQTT_CLIENT_COUNT).each do |i| # create 1 to N mosquitto mqtt brokes nodes
    node_ip_addr = "#{MQTT_CLIENT_NODES[:subnet]}#{MQTT_CLIENT_NODES[:ip_offset] + i}"
    node_name = "#{MQTT_CLIENT_NODES[:nameprefix]}#{i}"
    config.vm.define node_name do |s| # define one particular node
      s.vm.network "private_network", ip: node_ip_addr
      s.vm.hostname = node_name
      s.vm.provider "docker" do |d|
        d.build_dir = "./mqtt_client"
        d.name = node_name
        d.has_ssh = true
      end
    end
  end
end
# EOF

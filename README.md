# KIV-DS-4HW
Fourth HW assigned in KIV/DS

1) Popis skladby kontejnerů

V implementaci je téměř důkladně dodržena architektura, jež byla navržena v rámci 3. samostatné práce (viz https://github.com/drtinao/KIV-DS-3HW). Jediným rozdílem mezi navrženou architekturou a implementací je nepřítomnost zpráv odesílaných přes MQTT v rámci Apache ZooKeeper. Po bližším přezkoumání jsem totiž zjistil, že by to mělo za následek zbytečný overhead a riziko ztráty zpráv je minimální (máme 3-6 brokerů).

1.a) MQTT broker

Broker pro své služby používá open-source MQTT brokera Mosquitto a program psaný v Pythonu. Pro komunikaci se ZooKeeperem je využita knihovna Kazoo.

Princip fce: po zapnutí Mosquitto se spustí program v Pythonu, jež běží na pozadí a komunikuje se ZooKeeperem. V tomto případě je v ZooKeeperu vytvořen pouze ephemeral (dočasný) uzel, který reprezentuje běžícího MQTT brokera, ke kterému se může MQTT klient připojit. Uzel je vytvořen v cestě /mqtt_brokers_list/mqtt_node000000000x, kde x reprezentuje pořadí vytvoření brokera (sequential uzel). Hodnotou je v tomto případě IP adresa brokera. Spojení se ZooKeeperem NENÍ po vytvoření uzlu ukončeno - tím je zajištěno, že ephemeral uzel zůstane viditelný po celou dobu, kterou broker poběží a po jeho ukončení zmizí.

Jednotlivé brokery jsou mezi sebou propojeny ("bridge"), tedy z pohledu klienta poskytují ekvivalentní služby.

Počet MQTT brokerů je možno změnit pomocí konstanty "MQTT_BROKER_COUNT" v rámci Vagrantfile. Výchozí volba je 3, program umožňuje počet brokerů libovolně navýšit. MQTT klienti se vždy připojí k brokerovi, který je nejméně vytížen.

1.a) MQTT klient

Klient využívá Kazoo pro komunikaci se ZooKeeperem a Paho pro operace s MQTT.

Princip fce: klient se připojí k některému ze ZooKeeper serverů. Následně zjistí, který MQTT broker je nejméně obsazený a k tomu se připojí. Pokud žádný z brokerů nikoho neobsluhuje, připojí se k prvnímu brokeru v seznamu. Seznam brokerů je reprezentován potomky uzlu /mqtt_brokers_list. Pokud je připojení úspěšné, vytvoří klient ephemeral uzel v /mqtt_clients_list/xmqtt_client000000000y - kde x reprezentuje číslo brokera (shodné s /mqtt_brokers_list) a y pořadí klienta (uzel je opět sequential).

V případě výpadku spojení je ze ZooKeeperu odstraněn uzel reprezentující klienta a celý proces výběru vhodného brokera se opakuje.

Počet MQTT brokerů je možno změnit pomocí konstanty "MQTT_CLIENT_COUNT" v rámci Vagrantfile. Výchozí počet je 5, možno navýšit.

1.c) ZooKeeper

Jak je již zřejmé z předchozího popisu, ZooKeeper je v programu použit pro evidování aktivních brokerů a klientů. Na základě získaných informací pak probíhá výběr vhodného brokera, kterého klient využije.

ZooKeeper uzly mají, dle zadání, fixní počet - 3. Jeden je tedy leader, zbylé dva uzly jsou followeři. Zda je obsah uzlů konzistentní se dá snadno otestovat napojením do jednotlivých kontejnerů a spuštění ZooKeeper klienta skriptem zkCli.sh. Tento způsob byl použit i během ladění distribuovaného systému.

2) Implementace healthchecku + testování

Níže je uveden popis implementace healtchecku u komponent, kde byl vyžadován.

2.a) ZooKeeper

V intervalu 5s je spuštěn příkaz "/usr/local/zookeeper/bin/zkServer.sh status | grep "Mode:" || exit 1". Skript zjistí, zda ZooKeeper služba běží (grep "Mode:"). Pokud by služba neběžela, vypíše testovací skript řádku začínající "Error:", což by mělo za následek přechod stavu na "unhealthy".

Test:
1) docker exec -it zoonode-1 /bin/bash - napojím se do kontejneru
2) pkill java - v rámci kontejneru "zneškodním" proces Javy, na které ZooKeeper staví -> nefunguje
3) exit - uzavření interakce s kontejnerem
4) docker ps - kontrola, zda je "zoonode-1" ve stavu unhealthy

Po provedení testu kontejner sestavy skončil v očekáváném stavu "unhealthy", zbytek uzlů nadále pracoval korektně.

2.b) MQTT broker

V intervalu 5s je spuštěn příkaz "pgrep mosquitto || exit 1", který zjistí, zda proces služby Mosquitto běží či nikoliv. Pokud proces neexistuje, přejde kontejner do stavu "unhealthy".

Test:
1) docker exec -it mqtt-broker-node-1 /bin/bash - napojím se do kontejneru
2) pkill mosquitto - "zneškodnění" procesu Mosquitta
3) exit - uzavření interakce s kontejnerem
4) docker ps - kontrola, zda je "mqtt-broker-node-1" ve stavu unhealthy

Během mého testování se po provedení uvedených kroků kontejner vyskytl ve stavu "unhealthy" a klienti, které na něj byli připojeni, provedli přepojení na jiný uzel.

3) Spuštění aplikace

Pro spuštění je potřeba mít nainstalován Vagrant a Docker. Poté stačí v kořenovém adresáři pouze zadat příkaz „vagrant up“ a aplikace bude sestavena / spuštěna. Program následně běží do té doby než je ukončen (např. ctrl + c). V terminálu lze následně vidět zprávy, které jsou vysílány / přijímány jednotlivými klienty. Při výpadku některého z brokerů, jež byl využíván klientem, vypisuje klient informace o výpadku spojení / průběho přechodu na jiného brokera.

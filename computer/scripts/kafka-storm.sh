#!/bin/bash

./bin/storm nimbus     # master
./bin/storm supervisor # worker
./bin/storm ui

./bin/zookeeper-server-start.sh config/zookeeper.properties
./bin/kafka-server-start.sh config/server.properties
./bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test
./bin/kafka-topics.sh --list --zookeeper localhost:2181

# ./bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test
# ./bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning

java -cp .:lib/* sk.test.Demo localhost:2181 test /brokers storm-consumer
java -cp .:lib/* sk.test.DemoProducer test

javac -cp ../kafka_2.12-0.11.0.0/libs/kafka_2.12-0.11.0.0.jar:../apache-storm-1.1.0/lib/storm-core-1.1.0.jar:../kafka_2.12-0.11.0.0/libs/kafka-streams-0.11.0.0.jar:/root/.m2/repository/org/apache/storm/storm-kafka/1.0.1/storm-kafka-1.0.1.jar src/main/java/sk/test/*
javac -cp ../kafka_2.12-0.11.0.0/libs/kafka-clients-0.11.0.0.jar src/main/java/sk/test/DemoProducer.java

cat > dumps <<EOF
[root@localhost sk]# cat src/main/java/sk/test/Demo.java 
package sk.test;

import java.util.HashMap;

import org.apache.storm.LocalCluster;
import org.apache.storm.kafka.BrokerHosts;
import org.apache.storm.kafka.KafkaSpout;
import org.apache.storm.kafka.SpoutConfig;
import org.apache.storm.kafka.StringScheme;
import org.apache.storm.kafka.ZkHosts;
import org.apache.storm.spout.SchemeAsMultiScheme;
import org.apache.storm.topology.TopologyBuilder;

/**
 * @author Amit Kumar
 */
public class Demo {
	
	public static void main(String[] args) {
		// Log program usages and exit if there are less than 4 command line arguments
		if(args.length < 4) {
			System.out.println("Incorrect number of arguments. Required arguments: <zk-hosts> <kafka-topic> <zk-path> <clientid>");
			System.exit(1);
		}
		
		// Build Spout configuration using input command line parameters
		final BrokerHosts zkrHosts = new ZkHosts(args[0]);
		final String kafkaTopic = args[1];
		final String zkRoot = args[2];
		final String clientId = args[3];
		final SpoutConfig kafkaConf = new SpoutConfig(zkrHosts, kafkaTopic, zkRoot, clientId);
		kafkaConf.scheme = new SchemeAsMultiScheme(new StringScheme());

		// Build topology to consume message from kafka and print them on console
		final TopologyBuilder topologyBuilder = new TopologyBuilder();
		// Create KafkaSpout instance using Kafka configuration and add it to topology
		topologyBuilder.setSpout("kafka-spout", new KafkaSpout(kafkaConf), 1);
		//Route the output of Kafka Spout to Logger bolt to log messages consumed from Kafka
		topologyBuilder.setBolt("print-messages", new TestBolt()).globalGrouping("kafka-spout");
		
		// Submit topology to local cluster i.e. embedded storm instance in eclipse
		final LocalCluster localCluster = new LocalCluster();
		localCluster.submitTopology("kafka-topology", new HashMap<>(), topologyBuilder.createTopology());
	}
}
[root@localhost sk]# cat src/main/java/sk/test/TestBolt.java 
package sk.test;

import org.apache.storm.topology.BasicOutputCollector;
import org.apache.storm.topology.OutputFieldsDeclarer;
import org.apache.storm.topology.base.BaseBasicBolt;
import org.apache.storm.tuple.Fields;
import org.apache.storm.tuple.Tuple;

public class TestBolt extends BaseBasicBolt{
	
	private static final long serialVersionUID = 1L;

	@Override
	public void execute(Tuple input, BasicOutputCollector collector) {
		System.out.println(input.getString(0));
	}

	@Override
	public void declareOutputFields(OutputFieldsDeclarer declarer) {
		declarer.declare(new Fields("message"));
	}
}
[root@localhost sk]# cat src/main/java/sk/test/DemoProducer.java 
package sk.test;

import java.util.Properties;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;

public class DemoProducer {
   
   public static void main(String[] args) throws Exception{
      
      // Check arguments length value
      if(args.length == 0){
         System.out.println("Enter topic name");
         return;
      }
      
      //Assign topicName to string variable
      String topicName = args[0].toString();
      
      // create instance for properties to access producer configs   
      Properties props = new Properties();
      
      //Assign localhost id
      props.put("bootstrap.servers", "localhost:9092");
      
      //Set acknowledgements for producer requests.      
      props.put("acks", "all");
      
      //If the request fails, the producer can automatically retry,
      props.put("retries", 0);
      
      //Specify buffer size in config
      props.put("batch.size", 16384);
      
      //Reduce the no of requests less than 0   
      props.put("linger.ms", 1);
      
      //The buffer.memory controls the total amount of memory available to the producer for buffering.   
      props.put("buffer.memory", 4096000);
      
      props.put("key.serializer", 
         "org.apache.kafka.common.serialization.StringSerializer");
         
      props.put("value.serializer", 
         "org.apache.kafka.common.serialization.StringSerializer");
      
      Producer<String, String> producer = new KafkaProducer
         <String, String>(props);
            
      for(int i = 0; i < 10; i++)
         producer.send(new ProducerRecord<String, String>(topicName, 
            Integer.toString(i), Integer.toString(i)));
               System.out.println("Message sent successfully");
               producer.close();
   }
}
EOF

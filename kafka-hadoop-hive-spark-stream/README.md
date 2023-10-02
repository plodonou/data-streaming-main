# Kafka + Hadoop + Hive + Spark Streaming Example

```bash
~$ ssh-keygen -t rsa
~$ cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

Then, try SSH-ing into the machine (type `exit` to quit the SSH session and return)

```bash
~$ ssh localhost
```

With Hadoop configured and SSH setup, we can start the Hadoop cluster and test the installation.

```bash
~$ hdfs namenode -format
~$ start-dfs.sh
```

NOTE: These commands should be available anywhere since we added them to the PATH during configuration. If you're having troubles, `hdfs` and `start-dfs` are located in `hadoop/bin` and `hadoop/sbin`, respectively.

Finally, test that Hadoop was correctly installed by checking the Hadoop Distributed File System (HDFS):

```bash
~$ hadoop fs -ls /
```

If this command doesn't return an error, then we can continue!

---

```bash
~$ hive --service metastore
```

Now, enter the Hive shell with the `hive` command

```bash
~$ hive

 ...

hive>
```

Make the database for storing our Twitter data:

```bash
hive> CREATE TABLE tweets (text STRING, words INT, length INT)
    > ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\|'
    > STORED AS TEXTFILE;
```

You can use `SHOW TABLES;` to double check that the table was created.

---

```bash
~$ pip3 install pyspark
```

Check with

```bash
~$ pip3 list | grep spark
```

Now we need to add the Spark /bin files to the path, so open up `.bashrc` and add the following

```bash
export PATH=$PATH:/home/<USER>/spark/bin
export PYSPARK_PYTHON=python3
```

By setting the `PYSPARK_PYTHON` variable, we can use PySpark with Python3, the version of Python we have been using so far.

After running `source .bashrc`, try entering the PySpark shell

```bash
~$ pyspark

 ...

Using Python version ....
SparkSession available as 'spark'.
>>>
```

### Stream Producer

As mentioned previously, we are going to create a stream of Tweets. This requires a set of API keys available from a Twitter developer account. This is free, but often takes time to get approved. The process of optaining API keys is pretty simply, plus I'm sure there are resources out there if you get stuck.

- #### OPTION 1

  If you have Twitter API keys, open a new Python file on your VM with whatever name you like, and paste in the contents of `tweet_stream.py` found in the `files/` folder of this repo.

  You'll need to add your API keys on lines 35-39, as well as install the Twitter Python package with `pip3 install tweepy`

- #### OPTION 2

  If you don't have Twitter API keys, you can simulate "fake tweets". Open a new Python file on your VM and give it a name, then paste in the contents of `fake_tweet_stream.py` from the `files/` folder of this repo.

  Depending on your Linux distro, you should have a "wordlist" located somewhere in the `/usr/share` directory. My distro had one located in `/usr/share/dict/words`. Edit line 11 of this file to match your distro.

### Stream Consumer + Spark Transformer

Open a new Python file on your VM and give it a name. Paste in the contents of `transformer.py` found in the `files/` folder of this repo.

---

## Run the code

Now we are ready to run the example. Since we will be running multiple processes at once, we will have several terminals open at once. If your terminal emulator supports tabs, I recommend using that, but seperate terminal windows also works fine.

---

- ### Terminal 1 -- Zookeeper

In your first terminal window/tab, we need to start a Zookeeper instance. This is required for running a Kafka cluster

```bash
~$ cd kafka/
~/kafka$ bin/zookeeper-server-start.sh config/zookeeper.properties
```

This will write a lot of output to the console. As long as you don't hit an error and are returned to the prompt, it should be working. Keep this process running, and open a new terminal window/tab.

---

- ### Terminal 2 -- Kafka Broker

Now we need to start the Kafka broker.

```bash
~$ cd kafka/
~/kafka$ bin/kafka-server-start.sh config/server.properties
```

This will also write a lot of output to the console. If you didn't hit an error, keep this server running and open a new terminal.

---

- ### Terminal 3 -- Kafka Config

Now that we have our Kafka cluster running, we need to create the topic that will hold our tweets.

First check if any topics exist on the broker (this should return nothing if you just started the server)

```bash
~/kafka$ bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

Now make a new topic named `tweets`

```bash
~/kafka$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic tweets
```

Run the `--list` command from above to make sure the `tweets` topic was successfully created.

You can either close this terminal, or just keep it open and use it for the next step.

---

- ### Terminal 4 -- Hive Metastore

```bash
~$ hive --services metastore
```

There shouldn't be much output besides a message that says the metastore server has started.

Keep this terminal running and open up a new one.

---

- ### Terminal 5 -- Hive

In order to make sure the transformed data is being stored in Hive, we need to enter the Hive shell so that we can query the tables. Write a query to count the records in the tweets table. This should return nothing, but as we start the stream producer / consumer, we can use the up-arrow to run this query again to check if the data is coming through.

```bash
~$ hive

 ...

hive> use default;
hive> select count(*) from tweets;
```

Keep this one running and open up a new terminal.

---

- ### Terminal 6 -- Stream Producer

In this new terminal, we are going to run the stream producer. Mine is named `tweet_stream.py`, but just use whatever you named yours.

If want to change the file permissions with `chmod 755 tweet_stream.py`, you can run the stream producer with a simple `./`

```bash
~$ ./tweet_stream.py
```

If not, just run it with `python3`

```bash
~$ python3 tweet_stream.py
```

This script should produce output to the console everytime a tweet is sent to the Kafka cluster, so you should be able to know whether or not the stream producer is working. Keep this running and open up a new terminal.

---

- ### Terminal 7 -- Stream Consumer + Spark Transformer

Now we are ready to run the consumer. Since we want to run it as a Spark job, we'll use `spark-submit`. NOTE: I moved my extra JAR to the home directory, but if yours is in a different location, you'll need to provide the correct path.

```bash
~$ spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.4.3.jar transformer.py
```

This should produce a lot of logging output. Keep this running as long as you want the example to be running.

---

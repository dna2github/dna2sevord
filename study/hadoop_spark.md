# Hadoop

### port

(`iptables -A INPUT -p tcp --dport 0000 -j ACCEPT`)

- 9000 NameNode (hdfs)
- 9866 DataNode (hdfs)
- 8031 ResourceManager (yarn)
- 8032 (yarn master)
- 8040 (yarn worker)

- 8042 YARN worker Web UI
- 9870 Hadoop Web UI
- 9864 DataNode Web UI
- 8088 YARN Web UI

### cmd

- `hdfs namenode -format`
- `hdfs dfsadmin -report`
- `hdfs dfsadmin -refreshNodes`
- `hdfs dfs ...`

### tips

- extra config required in hadoop-env.sh

```
# HDFS_NAMENODE_USER by default in hadoop-env.sh
export HDFS_NAMENODE_USER=user

# in SOME-env.sh, but can add in hadoop-env.sh
export HDFS_DATANODE_USER=user
export HDFS_SECONDARYNAMENODE_USER=user
export YARN_RESOURCEMANAGER_USER=user
export YARN_NODEMANAGER_USER=user
```

- use hostname instead of ip for /etc/hadoop/workers; otherwise, can only find localhost datanode
- open 9000, 8031, 9864 | 9866, 8032 for cluster/client usage
- make sure network available from worker to master (port >10000); otherwise, YARN cannot allocate resources to worker
- before /sbin/start-all.sh, make sure ssh without password to all machines
   - `ssh-keygen`
   - `ssh-copy-id -i ~/.ssh/id_rsa.pub user@machine`

ref: https://weilu2.github.io/2018/10/30/Hadoop%E9%9B%86%E7%BE%A4%E9%83%A8%E7%BD%B2%E6%96%B9%E6%A1%88/

ref: https://juejin.cn/post/6844903828622409736


# Spark

### port

- 7077 Spark master communication port
- 8080 Spark master Web UI
- 8081 Spark slave Web UI

### minio (s3)

ref: https://www.jitsejan.com/setting-up-spark-with-minio-as-object-storage.html

```
from pyspark import SparkContext, SparkConf, SQLContext
conf = (
    SparkConf()
    .setAppName("Spark minIO Test")
    .set("spark.hadoop.fs.s3a.endpoint", "http://localhost:9091")
    .set("spark.hadoop.fs.s3a.access.key", os.environ.get('minIO_ACCESS_KEY'))
    .set("spark.hadoop.fs.s3a.secret.key", os.environ.get('minIO_SECRET_KEY'))
    .set("spark.hadoop.fs.s3a.path.style.access", True)
    .set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
)
sc = SparkContext(conf=conf).getOrCreate()
sqlContext = SQLContext(sc)

print(sc.wholeTextFiles('s3a://path/to/test.txt').collect())
# Returns: [('s3a://path/to/test.txt', 'Some text\nfor testing\n')]
path = "s3a://path/to/test.txt"
rdd = sc.parallelize([('Mario', 'Red'), ('Luigi', 'Green'), ('Princess', 'Pink')])
rdd.toDF(['name', 'color']).write.csv(path)
```

### cmd

- pyspark: `import pyspark.sql.types as types; df.withColumn(col, df[col].cast(types.FloatType()))`
- pyspark: `df.agg({col: 'max'}).collect()[0]`
- pyspark: `df.select(col).distinct() -> .count() / .collect() / .show()`

### common

```
from pyspark.ml.feature import VectorAssembler
# _c42 can be string, others cannot
dfx = a.transform(df).drop(*['_c' + str(i) for i in range(42)]).withColumnRenamed('_c42', 'label')
# then get label: string and features: vector
# and follow: https://spark.apache.org/docs/latest/ml-classification-regression.html#decision-tree-classifier

# old way
import pyspark.sql.functions -> udf
import pyspark.sql.types -> FloatType, StringType
import pyspark.sql -> Row

import pyspark.mllib.regression -> LabeledPoint

df.select( udf(lambda x: x + 1, FloatType())(col).cast(StringType()) ).show()
df.agg({col: 'max'}).collect()[0]
df.select(col).distinct().count()
spark.createDataFrame()
df.rdd
rdd.take(5)
rdd.map(lambda x: LabeledPoint(x[0], [x[1:]]))
...
```

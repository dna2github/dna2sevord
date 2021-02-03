### port

(`iptables -A INPUT -p tcp --dport 0000 -j ACCEPT`)

- 9000 NameNode (hdfs)
- 8031 ResourceManager (yarn)

- 9870 Hadoop Web UI
- 9864 DataNode Web UI
- 8088 YARN Web UI

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
- before /sbin/start-all.sh, make sure ssh without password to all machines
   - `ssh-keygen`
   - `ssh-copy-id -i ~/.ssh/id_rsa.pub user@machine`

ref: https://weilu2.github.io/2018/10/30/Hadoop%E9%9B%86%E7%BE%A4%E9%83%A8%E7%BD%B2%E6%96%B9%E6%A1%88/

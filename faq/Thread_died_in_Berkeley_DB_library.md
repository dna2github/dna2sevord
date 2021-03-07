# How to resolve "Thread died in Berkeley DB library"

ref: https://cloudlinux.zendesk.com/hc/en-us/articles/115004075294-Fix-rpmdb-Thread-died-in-Berkeley-DB-library

```
rpmdb: Thread/process 277623/140429100390144 failed: Thread died in Berkeley DB library
error: db3 error(-30974) from dbenv->failchk: DB_RUNRECOVERY: Fatal error, run database recovery
error: cannot open Packages index using db3 -  (-30974)
error: cannot open Packages database in /var/lib/rpm
CRITICAL:yum.verbose.cli.yumcompletets:Yum Error: Error: rpmdb open failed
```

solution:

```
mkdir /var/lib/rpm/backup
cp -a /var/lib/rpm/__db* /var/lib/rpm/backup/
rm -f /var/lib/rpm/__db.[0-9][0-9]*
rpm --quiet -qa
rpm --rebuilddb
yum clean all
```

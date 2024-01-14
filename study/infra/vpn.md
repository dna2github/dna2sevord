set up SS and KCPTUN, SS listen at localhost, KCPTUN listen at 0.0.0.0 and connect to SS

```
#!/bin/bash

SELF=$(cd `dirname $0`; pwd)
KCP=/path/to/kcp_client
SS=/path/to/sslocal
KCPHOST= # remote kcp server: 1.2.3.4:5678
KCPKEY=  # remote kcp server password
SSKEY=   # remote ss server password

_term() {
   echo "Exiting; Stop KCPTUN+SS ..."
   echo "kill kcptun: $KCPPID"
   kill $KCPPID
   echo "kill ss: $SSPID"
   kill $SSPID
   echo "[DONE]"
   exit 0
}

trap _term TERM INT

echo "Starting; run KCPTUN+SS ..."

echo ====================== `date` >> $SELF/kcp.log
$KCP --localaddr 127.0.0.1:31001 --remoteaddr $KCPHOST --key $KCPKEY >> $SELF/kcp.log 2>&1 &
KCPPID=$!
echo "KCPTUN: $KCPPID"

sleep 3

echo ====================== `date` >> $SELF/ss.log
$SS -s 127.0.0.1 -p 31001 -b 127.0.0.1 -l 11080 -k $SSKEY > $SELF/ss.log 2>&1 &
SSPID=$!
echo "SS: $SSPID"

echo "Running ..."

while true; do
   sleep 1
done
```

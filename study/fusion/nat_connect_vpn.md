# VMware Fusion using NAT in VM to connect to host company network

BigSur disallow external kext loaded; vmnet3 has limited ability to config NAT;
it creates a virtual NIC of `bridge100`. you can get DNS response but cannot visit resource via company network.


```
ifconfig
```

whose name is `utunX` e.g. `utun0` possibly the interface for company network.

```
sudo pfctl -a com.apple.internet-sharing/shared_v4 -s nat
```
use `pfctl` to get NAT config

```
nat on en0 inet from 192.168.29.0/24 to any -> (en0:0) extfilter ei
no nat on bridge100 inet from 192.168.29.1 to 192.168.29.0/24
```

you can see by default `bridge100` connect to internet via `en0`

backup the output to `backup.conf` and duplicate one as `newrules.conf` like:

```
nat on utun8 inet from 192.168.29.0/24 to any -> (utun8) extfilter ei
nat on en0 inet from 192.168.29.0/24 to any -> (en0:0) extfilter ei
no nat on bridge100 inet from 192.168.29.1 to 192.168.29.0/24
```

add NAT rule for `utun8` (example) and apply the new rules:

```
sudo pfctl -a com.apple.internet-sharing/shared_v4 -N -f newrules.conf
```

then you can use VMware Fusion to visit company network resources.

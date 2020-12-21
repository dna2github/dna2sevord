### build Linux distribution

```
ARCH=um make menuconfig
ARCH＝um make tar-pkg

# extract tarball to /path
# compile busybox and
# prepare initrd resources to /path

# edit /path/etc/init.d/rcS
cat > /path/etc/init.d/rcS <<EOF
mount proc
mount sysfs
EOF

cd /path && find . | cpio -o -H newc | gzip -c > initrd.img
```

### on Linux Host

```
# add TUN/TAP
ip tuntap add um0tap mode tap
ifconfig um0tap 10.0.1.1 netmask 255.255.255.0 up

# forward channel: tuntap --> eth0
iptables -t nat -A POSTROUTING -s 10.0.1.0/24 -o eth0 -j MASQUERADE
echo 1 > /proc/sys/net/ipv4/ip_forward
route add -host 10.0.1.1 dev um0tap
echo 1 > /proc/sys/net/ipv4/conf/um0tap/proxy_arp
arp -Ds 10.0.1.1 eth0 pub
```

run User Mode Linux:

```
./linux initrd=initrd.img mem=64M eth0=tuntap,um0tap,,10.0.1.101
```

### on User Mode Linux:

```
ifconfig eth0 10.0.1.101 netmask 255.255.255.0 up
ifconfig lo up
route add default gw 10.0.1.1
```

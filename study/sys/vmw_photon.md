```
# @photon
# /etc/systemd/network/....
# systemctl restart systemd-networkd
[Match]
Name=e*

[Network]
Address=10.182.44.000/24
Gateway=10.182.44.254
DNS=10.78.1.132
IPv6AcceptRA=no
```

```
# https://kb.vmware.com/s/article/81304
cd /etc/yum.repos.d/
sed  -i 's/dl.bintray.com\/vmware/packages.vmware.com\/photon\/$releasever/g' photon.repo photon-updates.repo photon-extras.repo photon-debuginfo.repo
# resolve: Error: 401 when downloading https://dl.bintray.com/vmware/photon_release_3.0_x86_64/repodata/repomd.xml
. Please check repo url.
```

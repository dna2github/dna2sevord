# How to install ubuntu

```
sudo apt install dnsmasq
sudo kill (dhcpd tftp ...; sudo netstat -tulpn)
# download iso e.g. 20.04
sudo mount ubuntu-20.04.2.0-desktop-amd64.iso /mnt
mkdir /opt/tftp
cp /mnt/EFI/install/* /opt/tftp/

sudo cat > /etc/dnsmasq.conf <<EOF
dns-port=0
interface=eth0
bind-interfaces
dhcp-range=192.168.1.200,192.168.1.250,255.255.255.0,2h
dhcp-option=3,192.168.1.1
dhcp-match=set:efi-x86_64,option:client-arch,7
dhcp-boot=tag:efi-x86_64,bootx64.efi
enable-tftp
tftp-root=/opt/tftp
EOF

sudo systemctl start dnsmasq
```

- connect pxe server host and target machine in the same router
- close router built-in DHCP server
- copy iso file into a USB disk and connect USB to target machine
- boot on target machine and do PXE boot, it will go to `grub` interactive mode

```
ls
# say usb disk at (hd0,msdos1)
loopback loop (hd0,msdos1)/ubuntu.iso
set root=(loop)
linux /casper/vmlinuz boot=casper iso-scan/filename=/ubuntu.iso
initrd /casper/initrd
boot
```

- after boot successfully, config ubuntu, remove USB disk and reboot target machine

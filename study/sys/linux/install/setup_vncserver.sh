#!/bin/bash

yum groupinstall "gnome desktop"
yum install tigervnc-server

cp /lib/systemd/system/vncserver\@.service /etc/systemd/system/vncserver\@\:1.service
sed -i 's|<USER>|root|' /etc/systemd/system/vncserver\@\:1.service
systemctl daemon-reload

firewall-cmd --permanent --zone=public --add-service vnc-server
firewall-cmd --reload
vncserver # to init password

systemctl enable 'vncserver@:1.service'
reboot
systemctl start 'vncserver@:1.service'

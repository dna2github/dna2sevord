#!/bin/bash
set -x

iptables -F
iptables -A INPUT -j ACCEPT
cat > /etc/yum.repos.d/mariadb.repo <<EOF
[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.1/centos7-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1
EOF
yum install -y MariaDB-server MariaDB-client
sed -i 's|#bind-address=0.0.0.0|bind-address=0.0.0.0|' /etc/my.cnf.d/server.cnf
service mysql start
cat > /root/config.sql <<EOF
use mysql;
GRANT ALL ON *.* to admin@'%' IDENTIFIED BY 'ch@ngemE';
FLUSH PRIVILEGES;
EOF
mysql -u root < /root/config.sql
rm -rf /root/setup.sh /root/config.sql

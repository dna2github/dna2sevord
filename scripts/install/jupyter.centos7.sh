#!/bin/bash
set -x

echo install nginx ...
yum install -y libcurl
yum install -y vim openssl-devel epel-release
yum install -y nginx

echo install python3.6 ...
wget --no-check-certificate https://centos7.iuscommunity.org/ius-release.rpm
yum install -y ius-release.rpm
sed -i 's|https://|http://|g' /etc/yum.repos.d/ius*
yum install -y python36u python36u-pip

echo install tensorflow and jupyter nootbook ...
pip3.6 install --upgrade pip
pip install jupyter tensorflow pandas keras

echo disable firewall ...
iptables -F
iptables -A INPUT -j ACCEPT

echo config server ...
mkdir -p /etc/nginx/ca
openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/nginx/ca/cert.key -out /etc/nginx/ca/cert.crt \
    -subj "/C=country/ST=state/L=location/O=org/OU=unit/CN=hostname"
sed -i 's|80|20001|g' /etc/nginx/nginx.conf
cat > /etc/nginx/conf.d/jupyter.conf <<EOF
server {
    listen 80;
    return 301 https://$host$request_uri;
}
server {
    listen 443 ssl;
    ssl on;
    ssl_certificate      /etc/nginx/ca/cert.crt;
    ssl_certificate_key  /etc/nginx/ca/cert.key;
    ssl_protocols        TLSv1 TLSv1.1 TLSv1.2;

    ssl_session_cache shared:SSL:1m;
    ssl_session_timeout  5m;

    ssl_ciphers  HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers   on;

    location ^~ /api/kernels {
      proxy_pass              http://127.0.0.1:10001;
      proxy_set_header        Host \$host;
      proxy_set_header        X-Real-IP \$remote_addr;
      proxy_set_header        X-Forwarded-For \$proxy_add_x_forwarded_for;
      proxy_set_header        X-Forwarded-Proto \$scheme;
      proxy_set_header        X-NginX-Proxy true;
      proxy_http_version 1.1;
      proxy_redirect off;
      proxy_buffering off;
      proxy_set_header Upgrade \$http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_read_timeout 86400;
    }

    location / {
      proxy_pass              http://127.0.0.1:10001;
      proxy_redirect          off;
      proxy_set_header        Host \$host;
      proxy_set_header        X-Real-IP \$remote_addr;
      proxy_set_header        X-Forwarded-For \$proxy_add_x_forwarded_for;
      proxy_set_header        X-Forwarded-Proto \$scheme;
      proxy_set_header        X-NginX-Proxy true;
    }

}
EOF
nginx

echo start jupyter server ...
mkdir -p /root/data
jupyter notebook --allow-root --no-browser --port 10001 --notebook-dir=/root/data --NotebookApp.token='' >/dev/null 2>&1 &

echo clean up ...
rm -rf /root/setup.sh /root/ius-release.rpm

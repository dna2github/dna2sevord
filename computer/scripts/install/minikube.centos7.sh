#!/bin/bash

set -ex

echo config system ...
setenforce 0
swapoff -a
iptables -F
iptables -A INPUT -j ACCEPT
sysctl net.bridge.bridge-nf-call-iptables=1
sysctl net.bridge.bridge-nf-call-ip6tables=1

echo install docker ...
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce
systemctl start docker

echo install local kubernetes ...
cd /usr/local/bin
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
chmod 755 kubectl
wget -O minikube https://github.com/kubernetes/minikube/releases/download/v0.28.0/minikube-linux-amd64
chmod 755 minikube
alias systemctl=/usr/bin/systemctl
which systemctl
minikube start --vm-driver=none

echo install nginx ...
yum install -y openssl-devel epel-release
yum install -y nginx
mkdir -p /etc/nginx/ca
openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/nginx/ca/cert.key -out /etc/nginx/ca/cert.crt \
    -subj "/C=UK/ST=CA/L=wdc/O=example/OU=ou/CN=hostname"
sed -i 's|80|20001|g' /etc/nginx/nginx.conf
DASHBOARD=`kubectl get pods --namespace=kube-system | grep kubernetes-dashboard | cut -d ' ' -f 1`
DASHBOARD_HOST=`kubectl describe pod $DASHBOARD --namespace=kube-system | grep IP | grep -o '[0-9]*[.][0-9]*[.][0-9]*[.][0-9]*'`
cat > /etc/nginx/conf.d/kube.conf <<EOF
server {
    listen 80;
    return 301 https://\$host\$request_uri;
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

    location / {
      proxy_pass              http://${DASHBOARD_HOST##}:9090;
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

rm -rf /root/setup.sh

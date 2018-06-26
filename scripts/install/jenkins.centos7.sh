#!/bin/bash
set -x

echo disable firewall ...
iptables -F
iptables -A INPUT -j ACCEPT

echo install docker ...
sysctl net.bridge.bridge-nf-call-iptables=1
sysctl net.bridge.bridge-nf-call-ip6tables=1
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce
systemctl start docker

echo install jenkins ...
JENKINS_VERSION=2.121.1-1.1
docker pull jenkins/jenkins:${JENKINS_VERSION}

echo config jenkins ...
mkdir -p /root/data /root/ref
chmod 777 /root/data /root/ref
mkdir -p /root/ref/temp /root/ref/init.groovy.d /root/data/plugins
wget --no-check-certificate http://example.com/test.hpi
mv test.hpi /root/data/plugins

cat > /root/ref/temp/plugins.txt <<EOF
git-client:2.7.0
git:3.6.4
gerrit-trigger:2.26.2
ldap:1.17
matrix-auth:2.1.1
ws-cleanup:0.34
workflow-aggregator:2.5
ssh-slaves:1.22
sonar-gerrit:2.0
sonar:2.6.1
update-sites-manager:2.0.0
node-iterator-api:1.5
statistics-gatherer:1.1.2
EOF
cat > /root/ref/temp/setup.sh <<EOF
/usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/temp/plugins.txt
EOF
cat > /root/ref/init.groovy.d/setup.groovy <<EOF
import hudson.security.GlobalMatrixAuthorizationStrategy;
import jenkins.model.Jenkins;

import hudson.util.Secret;
import hudson.security.LDAPSecurityRealm;
import hudson.security.SecurityRealm;
import jenkins.model.IdStrategy;
import jenkins.model.Jenkins;
import jenkins.security.plugins.ldap.*;

import jenkins.model.*
import hudson.security.*
import jenkins.install.InstallState

def instance = Jenkins.getInstance()

if (hudson.model.User.getAll()?.empty) {
  List admins = [
    'admin'
  ]

  def strategy = new hudson.security.GlobalMatrixAuthorizationStrategy()
  admins.each {
    strategy.add(hudson.model.Hudson.ADMINISTER, it)
  }

  // Add read permission for all users
  strategy.add(hudson.model.Item.READ,'anonymous')
  strategy.add(hudson.model.Item.DISCOVER,'anonymous')
  strategy.add(hudson.model.Hudson.READ,'anonymous')
  strategy.add(hudson.model.Item.READ,'authenticated')
  strategy.add(hudson.model.Item.DISCOVER,'authenticated')
  strategy.add(hudson.model.Hudson.READ,'authenticated')
  Jenkins.instance.setAuthorizationStrategy(strategy)
}


//println "--> creating local user 'admin'"
// Create user with custom pass
//def user = instance.getSecurityRealm().createAccount('admin', 'admin')
//user.save()

def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

if (!instance.installState.isSetupComplete()) {
  println '--> Neutering SetupWizard'
  InstallState.INITIAL_SETUP_COMPLETED.initializeState()
}

instance.save()


// ldap
if (hudson.model.User.getAll()?.empty) {
  String server = 'ldaps://ldaps.example.com'
  String rootDN = 'DC=example,DC=com'
  String userSearchBase = ''
  String userSearch = 'uid={0}'
  String groupSearchBase = ''
  String managerDN = ''
  Secret managerPassword = Secret.fromString('')
  boolean inhibitInferRootDN = false

  LDAPConfiguration configuration = new LDAPConfiguration(server, rootDN, false, managerDN, managerPassword);
  SecurityRealm ldap_realm = new LDAPSecurityRealm([configuration], false, null, IdStrategy.CASE_INSENSITIVE, IdStrategy.CASE_INSENSITIVE)
  Jenkins.instance.setSecurityRealm(ldap_realm)
}


// mailer
if (hudson.model.User.getAll()?.empty) {
  def descriptor = hudson.tasks.Mailer.DESCRIPTOR
  descriptor.setDefaultSuffix('@example.com');
  descriptor.setSmtpHost('smtp.example.com');
  descriptor.setUseSsl(false)
  descriptor.setCharset('UTF-8')
}
EOF
docker run -d \
      -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
      -p 50000:50000 \
      -v /root/ref:/usr/share/jenkins/ref \
      -v /root/data:/var/jenkins_home \
      --name jenkins \
      jenkins/jenkins
docker exec jenkins bash /usr/share/jenkins/ref/temp/setup.sh
chown -R 1000:1000 /root/data /root/ref
docker restart jenkins

echo install nginx ...
yum install -y openssl-devel epel-release
yum install -y nginx
mkdir -p /etc/nginx/ca
openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/nginx/ca/cert.key -out /etc/nginx/ca/cert.crt \
    -subj "/C=country/ST=state/L=location/O=org/OU=unit/CN=hostname"
JENKINS_HOST=`docker inspect jenkins | grep '"IPAddress"' | grep -o -E "[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+" | sort -u`
sed -i 's|80|20001|g' /etc/nginx/nginx.conf
cat > /etc/nginx/conf.d/jenkins.conf <<EOF
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

    location / {
      proxy_pass              http://${JENKINS_HOST}:8080;
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

echo clean up ...
rm -rf /root/setup.sh

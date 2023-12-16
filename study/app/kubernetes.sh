nimbus deploy ovf --memory=512 --cpus=1 kube-st0 /https/rdtoolutils/ovf/tcentos/tcentos.ovf

- Install docker
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
# yum-config-manager --enable docker-ce-edge docker-ce-test
yum install -y docker-ce
systemctl start docker
docker run hello-world

- Install Kubernetes
# cd /usr/local/bin
# curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
# chmod +x kubectl

cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
        https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
# Disabling SELinux by running setenforce 0 is required to allow containers to access the host filesystem,
# which is required by pod networks for example. You have to do this until SELinux support is improved in the kubelet.
setenforce 0
yum install -y kubelet kubeadm
systemctl enable kubelet && systemctl start kubelet

[master]
kubeadm init
kubeadm init --pod-network-cidr 10.3.0.0/16
# wait for message that show `kubeadm join --token <token>`
sysctl net.bridge.bridge-nf-call-iptables=1
[addition/network] kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/v0.8.0/Documentation/kube-flannel.yml

[slave]
kubeadm join --token <token>


export KUBECONFIG=/etc/kubernetes/admin.conf
kubectl get nodes


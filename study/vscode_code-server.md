# VSCode

# Code-Server

ref: https://github.com/cdr/code-server

```
build:

docker pull python
docker run --rm -it -v `pwd`:/opt/code-server python bash
# apt-get install -y build-essential pkg-config libx11-dev libxkbfile-dev libsecret-1-dev python3 jq rsync
# cd /opt
# wget https://nodejs.org/dist/v14.16.0/node-v14.16.0-linux-x64.tar.xz
# tar Jxf node-v14.16.0-linux-x64.tar.xz
# export PATH=$PATH:/opt/node-v14.16.0-linux-x64/bin
# npm config set python python3
# npm install -g yarn
# ./node_modules/.bin/yarn install
# cd /opt/code-server
# yarn install
# npm run build && npm run build:vscode && npm run release && npm run release:standalone
```

```
run:
PASSWORD='shitest' ./bin/code-server --auth password \
   --bind-addr <ip>:19443 \
   --user-data-dir ./local/user \
   --extensions-dir ./local/ext \
   --disable-telemetry --disable-update-check

[node]:bin/code-server ->
   [node]:bin/code-server ->
      [node]:lib/vscode/out/vs/server/fork ->
         [node]:lib/vscode/out/bootstrap-fork(--type=extensionHost)
```

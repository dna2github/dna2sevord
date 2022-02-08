# sourcegraph microservices

```
      o- frontend
      o- worker
      o- repo-updater
      o- gitserver
      o- searcher
      o- symbols
      o- web
      x- caddy (HTTPS) -> nginx
      o- docsite
      o- syntax-highlighter
      o- github-proxy
      o- zoekt-indexserver-0
      o- zoekt-indexserver-1
      o- zoekt-webserver-0
      o- zoekt-webserver-1

    [
      { "Name": "frontend", "Host": "127.0.0.1:6063" },
      { "Name": "enterprise-frontend", "Host": "127.0.0.1:6063" },
      { "Name": "gitserver", "Host": "127.0.0.1:6068" },
      { "Name": "searcher", "Host": "127.0.0.1:6069" },
      { "Name": "symbols", "Host": "127.0.0.1:6071" },
      { "Name": "repo-updater", "Host": "127.0.0.1:6074" },
      { "Name": "enterprise-repo-updater", "Host": "127.0.0.1:6074" },
      { "Name": "precise-code-intel-worker", "Host": "127.0.0.1:6088" },
      { "Name": "worker", "Host": "127.0.0.1:6089" },
      { "Name": "enterprise-worker", "Host": "127.0.0.1:6089" },
      { "Name": "executor-codeintel", "Host": "127.0.0.1:6092" },
      { "Name": "executor-batches", "Host": "127.0.0.1:6093" },
      { "Name": "zoekt-indexserver-0", "Host": "127.0.0.1:6072" },
      { "Name": "zoekt-indexserver-1", "Host": "127.0.0.1:6073" },
      { "Name": "zoekt-webserver-0", "Host": "127.0.0.1:3070", "DefaultPath": "/debug/requests/" },
      { "Name": "zoekt-webserver-1", "Host": "127.0.0.1:3071", "DefaultPath": "/debug/requests/" }
    ]

# yarn docsite:serve

git clone git://github.com/sourcegraph/zoekt.git --depth=1
GO111MODULES=on go build -o dist/zoekt-archive-index cmd/zoekt-archive-index/{main.go,flowrate.go,archive.go}
GO111MODULES=on go build -o dist/zoekt-sourcegraph-indexserver cmd/zoekt-sourcegraph-indexserver/{sg.go,queue.go,meta.go,merge.go,index.go,cleanup.go,main.go}
GO111MODULES=on go build -o dist/zoekt-git-index cmd/zoekt-git-index/main.go
GO111MODULES=on go build -o dist/zoekt-merge-index cmd/zoekt-merge-index/main.go
GO111MODULES=on go build -o dist/zoekt-webserver cmd/zoekt-webserver/main.go

git clone git://github.com/sourcegraph/sourcegraph.git --depth=1
/workspace/sourcegraph/cmd/github-proxy#
GO111MODULE=on CGO_ENABLED=0 go build -trimpath -buildmode exe -tags dist -o ~/go/bin/github-proxy github-proxy.go

/workspace/sourcegraph/cmd/symbols#
GO111MODULE=on CGO_ENABLED=0 go build -trimpath -buildmode exe -tags dist -o ~/go/bin/symbols *.go

/workspace/sourcegraph/cmd/searcher#
GO111MODULE=on CGO_ENABLED=0 go build -trimpath -buildmode exe -tags dist -o ~/go/bin/searcher main.go

/workspace/sourcegraph/cmd/gitserver#
GO111MODULE=on CGO_ENABLED=0 go build -trimpath -buildmode exe -tags dist -o ~/go/bin/gitserver main.go

/workspace/sourcegraph/cmd/repo-updater#
GO111MODULE=on CGO_ENABLED=0 go build -trimpath -buildmode exe -tags dist -o ~/go/bin/repo-updater main.go

/workspace/sourcegraph/cmd/worker#
GO111MODULE=on CGO_ENABLED=0 go build -trimpath -buildmode exe -tags dist -o ~/go/bin/worker main.go

/workspace/sourcegraph/cmd/frontend#
bash pre-build.sh # /workspace/sourcegraph/ui/assets/…
GO111MODULE=on CGO_ENABLED=0 go build -trimpath -buildmode exe -tags dist -o ~/go/bin/frontend main.go

/workspace/sourcegraph/cmd/server#
GO111MODULE=on CGO_ENABLED=0 go build -trimpath -ldflags
   '-X github.com/sourcegraph/sourcegraph/internal/version.version=test0 -X github.com/sourcegraph/sourcegraph/internal/version.timestamp=1644328737' \
   -buildmode exe -installsuffix netgo -tags 'dist netgo' -o ~/go/bin/main.go main.go

/workspace/sourcegraph/docker-images/syntax-highlighter#
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh # rust
cargo test --release
cargo rustc --release
cp target/release/syntect_server ~/go/bin
git clone git://github.com/slimsag/http-server-stabilizer.git && cd http-server-stabilizer && git checkout v1.0.4 && go build -o ~/go/bin/http-server-stabilizer . && cd ..

```

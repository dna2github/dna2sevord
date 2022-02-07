# build static binary in golang

```
CGO_ENABLED=0 go build ...

go build -ldflags="-extldflags=-static" ...
```

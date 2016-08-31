#!/bin/bash

cd `dirname $0`
GOPATH=`pwd` go build langparser
mkdir -p bin
mv langparser bin/langparser

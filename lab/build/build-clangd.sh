#!/bin/bash

# ref: https://gist.github.com/jakob/929ed728c96741a119798647a32618ca

set -e

mkdir clangd
cd clangd/
svn co http://llvm.org/svn/llvm-project/llvm/trunk llvm

cd llvm/tools
svn co http://llvm.org/svn/llvm-project/cfe/trunk clang
cd ../..

cd llvm/tools/clang/tools
svn co http://llvm.org/svn/llvm-project/clang-tools-extra/trunk extra
cd ../../../..

mkdir build
cd build
cmake -G "Unix Makefiles" ../llvm
make clangd

# Add binary to your $PATH
echo $PWD/bin | sudo tee /etc/paths.d/clangd

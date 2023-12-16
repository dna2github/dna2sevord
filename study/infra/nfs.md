# NFS

### get file without mounting

```
git clone https://github.com/sahlberg/libnfs
cd libnfs
libtoolize
aclocal
autoheader
autoconf
automake --add-missing
./configure --prefix=`pwd`/dist
make -j8
make install

./dist/bin/nfs-ls nfs://127.0.0.1/path/to/export
./dist/bin/nfs-cp nfs://127.0.0.1/path/to/export/file/name ./name
```

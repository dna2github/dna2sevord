```
proot -S `pwd` -b /tmp:/host-rootfs -w / /bin/bash

# run ARM on x86_64
# @require qemu-user-static
proot -S `pwd` -b /tmp:/host-rootfs -w / -q qemu-aarch64-static /bin/bash
```

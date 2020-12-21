1. save source file as `spin.c`

reference: https://github.com/docker-library/hello-world/blob/master/hello.c

```c
#include <unistd.h>
#include <sys/syscall.h>
#include <signal.h>

const char message[] = "spin\n";

void handler_ctrl_c(int sig) {
   syscall(SYS_exit, 0);
}

void _start() {
   signal(SIGINT, handler_ctrl_c);
   signal(SIGTERM, handler_ctrl_c);
   syscall(SYS_write, 1, message, sizeof(message) - 1);
   while (1) sleep(1);
   syscall(SYS_exit, 0);
}
```

```
yum install glibc-static
gcc -o spin spin.c -static -Os -nostartfiles -fno-asynchronous-unwind-tables
```

2. write Dockerfile.

```
FROM scratch
COPY spin /
CMD ["/spin"]
```

3. build a base container image with running `docker build -t spin/scratch .` (about 7KB image)

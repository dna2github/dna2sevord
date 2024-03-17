```
subsystem
- filesystem
   - struct
      - superblock
      - inode
      - dentry
      - file (file_operations)
      - address_space (address_space_operations)
   - cache
      - slab
   - i/o scheduler
      - CFQ          (fair disk bandwidth)
      - Deadline     (prevent starvation)
      - Noop         (FIFO, better for SSD)
      - Anticipatory (reduce seek operation)
- network
    - netfilter
    - protocol
    - transport
    - data link
    - device
- schedule (cpu)
   - kthread / thread / process
   - context switch
   - SMP / AMP
   - CFS (red-black tree) / RT (linked list)
   - interrupt (+soft) / trap / signal
- memory
   - virtual memory
      - TLB
   - kmalloc / vmalloc
   - swap
- IPC
   - pipe
   - named pipe
   - semaphore
   - socket
   - message queue
   - shared memory (shmem)
   - binder/ashmem > android
- race codition
   - lock / semaphore
      - spin lock
      - rcu
      - rwlock
      - mutex
   - atom
- debug
   - printk / dmesg
   - oops (then kill) / panic (not to know how to kill)
   - kdump / kexec / crash
   - perf record / perf report
```

```
apt install kdump-tools
<yes> <yes> for kdump and kexec configure
reboot

sudo -s
sysctl -w kernel.sysrq=1
echo c > /proc/sysrq-trigger
```

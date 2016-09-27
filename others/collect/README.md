# Collect

### Colors

Xterm 256 Color: [origin](https://upload.wikimedia.org/wikipedia/en/1/15/Xterm_256color_chart.svg)

### GDB

GDB Debug for NodeJS/V8 [origin](https://gist.github.com/ofrobots/0bdcab89771221ace68d)

ref: [https://github.com/v8/v8/wiki/GDB-JIT-Interface](https://github.com/v8/v8/wiki/GDB-JIT-Interface)

### Algorithm

#### ACO for Shortest Path

Basic Ant Colony Optimization for Shortest Path.

Graph data is from the paper: [link](http://www.iasj.net/iasj?func=fulltext&aId=81491) Figure 1.1.

The perofrmance is not good, especially since each ant moves with seeing one forwarded deepth.

```
                (visible) --- (invisible)
               /
              /
  ant (now) ----- (visible) --- (invisble)
              \            \
               \            \
                (visible)    (invisible)
```

### Machine Leraning

#### Recurrent Nerual Network for adding small integer numbers

ref: [https://iamtrask.github.io/2015/11/15/anyone-can-code-lstm/](https://iamtrask.github.io/2015/11/15/anyone-can-code-lstm/)

The origin code is written in Python with NumPy. The new implementation is in Golang without 3rd lib.

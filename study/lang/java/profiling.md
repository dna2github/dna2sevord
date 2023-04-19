# Profiling

```
ref: https://bell-sw.com/announcements/2022/04/07/how-to-use-perf-to-monitor-java-performance/
ref: https://bell-sw.com/announcements/2020/07/22/Hunting-down-code-hotspots-with-JDK-Flight-Recorder/
```

```
sudo apt install openjdk-17-jdk
sudo apt install linux-tools-common linux-tools-`uname -r` # perf

java -XX:+PreserveFramePointer -cp . Workload
#        ^ allow perf to parse stack frames
# by default, perf reads /tmp/perf-<pid>.map
# jcmd <pid> Compiler.perfmap
# perf record -- java -XX:+DumpPerfMapAtExit Workload

sudo perf record -F <N/sec> -p <pid> -g -o samples.data -- sleep 10
cp samples.data analysis.data
perf report -i analysis.data

git clone https://github.com/brendangregg/FlameGraph.git
perf script -i analysis.data | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl > analysis.svg
```

```
# may need help with -XX:+UnlockDiagnosticVMOptions -XX:+DebugNonSafepoints
jcmd <pid> JFR.start settings=profile
sleep 10
jcmd <pid> JFR.dump name=1 filename=samples.jfr
wget https://bit.ly/2H3Uqck -O sjk.jar
java -jar sjk.jar ssa -f samples.jfr --flame > analysis.svg
```

```
jcmd <pid> ManagementAgent.start \
    jmxremote.authenticate=false \
    jmxremote.ssl=false \
    jmxremote.port=5555
```

# Debug Program with Debugger Especially with GDB

Today I started a hack game and the rule is really simple:

> Write a program with a die-loop, set a variable as a lock;
>
> Run the program; if the lock can be modified, win the game.

### Python

```python
import time

test = True
while test:
    print ("Hello World")
    time.sleep(1)
print("Bye-bye")
```

The python package `pyrasite` inspired me and it shows very cool skill with GDB.

```
python test.py &
ps -ef | grep python
gdb -p <pid>
> call PyGILState_Ensure()
> call PyRun_SimpleString("global test; test = False")
> call PyGILState_Release($1)
> c
```

Since there is a MacPro laptop, also try GDB but no codesign.
Create one in `Keychain Assistant`.
What a pity that it cannot recognize the format of python binary.
Then `file $(which python)`, it
reports of `fat mac binary format` containing x86_64 and x86 arch binary.
Need `lipo -thin x86_64 -output python.new $(which python)`.
And find `lldb`, thus `call (int) PyGILState_Ensure() ...`.

### NodeJS

```js
var test = true;

setInterval(function () {
  if (test) {
    console.log('Hello World');
  } else {
    console.log('Bye-bye');
    process.exit();
  }
}, 1000);
```

Not investigated into V8 engine deep, just use a quick way to resolve it. Next try is GDB.

```
node test.js &
ps -ef | grep node
node debug -p <pid>
> sb('test.js', 4);
> c
> repl
>>> test = false;
>>> ^C
> c
```

### Golang

```go
package main

import "time"
import "fmt"

func main() {
  test := true
  for test {
    fmt.Println("hello world!")
    time.Sleep(1000 * time.Millisecond)
  }
  fmt.Println("Bye-bye")
}
```

Did a cheat with `-gcflags`, will try direct act with GDB.

```
go build -gcflags "-N" test.go
./test &
ps -ef | grep test
gdb -p <pid>
> b test.go:9
> c
> info locals
> set test = false
> c
```

### Perl

### Ruby

### Java

```java
public class Test {
  private static boolean test = true;

  public static void main(String[] args) {
    while (test) {
      System.out.println("Hello World");
      try { Thread.sleep(1000); } catch (Exception e) {}
    }
    System.out.println("Bye-bye");
  }
}
```

This is a simple program for the game.
Need some gdb skill to get `function pointer` works.

```
javac Test.java
javap -c Test.class
java -cp . Test &
ps -ef | grep java
gdb -p <pid>
> set $pool = (long*)malloc(100)
> memset($pool, 0, 100)
> set $r = $pool
> set $jvm = $pool + 1
> set $jvm_api = $pool + 2
> set $env = $pool + 3
> set $env_api = $pool + 4
> call JNI_GetCreatedJavaVMs(0, 0, $r)
> call JNI_GetCreatedJavaVMs($jvm, *$r, $r)
> set $jvm = (long *) (*$jvm)
> set $jvm_api = (long *) (*$jvm)
> set $jvm_args = $pool + 5
> set *$jvm_args = 0x00010008
> set *($jvm_args + 1) = 0
> set *($jvm_args + 2) = 0
> set $$ATTACH_CURRENT_THREAD = 4
> set $$DETACH_CURRENT_THREAD = 5
> set $$FIND_CLASS = 6
> set $$GET_STATIC_FILED_ID = 144
> set $$GET_STATIC_BOOLEAN_FILED = 146
> set $$SET_STATIC_BOOLEAN_FIELD = 155
> p $jvm_api[$$ATTACH_CURRENT_THREAD]($jvm, $env, $jvm_args)
> set $env = (long *)*$env
> set $env_api = (long *)*$env
> p $test_klass = $env_api[$$FIND_CLASS]($env, "Test")
> p $test_klass_test = $env_api[$$GET_STATIC_FILED_ID]($env, $test_klass, "test", "Z")
> p $env_api[$$GET_STATIC_BOOLEAN_FILED]($env, $test_klass, $test_klass_test)
> p $env_api[$$SET_STATIC_BOOLEAN_FIELD]($env, $test_klass, $test_klass_test, 0)
> p $jvm_api[$$DETACH_CURRENT_THREAD]($jvm)
> c
```

For `lldb`, it is a little bit complex to call function pointer:
`((int (*)(long*, long**, long*))($jvm_api[4]))($jvm, &$env, $jvm_args)`

(Hard Problem)

```java
public class Test {
  public static void main(String[] args) {
    boolean test = true;
    while (test) {
      System.out.println("Hello World");
      try { Thread.sleep(1000); } catch (Exception e) {}
    }
    System.out.println("Bye-bye");
  }
}
```

- `javac Test.java`, `javap -c Test.class` and `java -cp . Test`
- `jmap -dump:file=hex <pid> && jhat hex` and browse at http://localhost:7000;
cannot find any reference to `test` (it is not an object and just an instance of `class Z`)
- `jstack <pid>` can get the tid of main thread (0x7fa412002000)
and `jhat hex` has the object of the `java.lang.Thread` of main (0x76ab05c40)
- `java.lang.Thread` has a native method `start0`
which invokes hotspot method of `JVM_StartThread` (hotspot/src/share/vm/prims/jvm.cpp),
there is a class `JavaThread` may contain the memory structure for local variables in thread stack.
- `Java HotSpot Serviceability Agent` can print detailed stack frame.
It is possible to find the address of a local variable.
See alos: http://stackoverflow.com/questions/38931255/change-variable-value-in-jvm-with-gdb/38947442#38947442

```java
import sun.jvm.hotspot.code.Location;
import sun.jvm.hotspot.code.LocationValue;
import sun.jvm.hotspot.code.NMethod;
import sun.jvm.hotspot.code.ScopeValue;
import sun.jvm.hotspot.code.VMRegImpl;
import sun.jvm.hotspot.debugger.Address;
import sun.jvm.hotspot.debugger.OopHandle;
import sun.jvm.hotspot.interpreter.OopMapCacheEntry;
import sun.jvm.hotspot.oops.Method;
import sun.jvm.hotspot.oops.Oop;
import sun.jvm.hotspot.runtime.CompiledVFrame;
import sun.jvm.hotspot.runtime.InterpretedVFrame;
import sun.jvm.hotspot.runtime.JavaThread;
import sun.jvm.hotspot.runtime.JavaVFrame;
import sun.jvm.hotspot.runtime.VM;
import sun.jvm.hotspot.runtime.VMReg;
import sun.jvm.hotspot.tools.Tool;

import java.util.List;

public class Frames extends Tool {

    @Override
    public void run() {
        for (JavaThread thread = VM.getVM().getThreads().first(); thread != null; thread = thread.next()) {
            System.out.println(thread.getThreadName() + ", id = " + thread.getOSThread().threadId());
            for (JavaVFrame vf = thread.getLastJavaVFrameDbg(); vf != null; vf = vf.javaSender()) {
                dumpFrame(vf);
            }
            System.out.println();
        }
    }

    private void dumpFrame(JavaVFrame vf) {
        Method method = vf.getMethod();
        String className = method.getMethodHolder().getName().asString().replace('/', '.');
        String methodName = method.getName().asString() + method.getSignature().asString();
        System.out.println("  # " + className + '.' + methodName + " @ " + vf.getBCI());

        if (vf.isCompiledFrame()) {
            dumpCompiledFrame(((CompiledVFrame) vf));
        } else {
            dumpInterpretedFrame(((InterpretedVFrame) vf));
        }
    }

    private void dumpCompiledFrame(CompiledVFrame vf) {
        if (vf.getScope() == null) {
            return;
        }

        NMethod nm = vf.getCode();
        System.out.println("    * code=[" + nm.codeBegin() + "-" + nm.codeEnd() + "], pc=" + vf.getFrame().getPC());

        List locals = vf.getScope().getLocals();
        for (int i = 0; i < locals.size(); i++) {
            ScopeValue sv = (ScopeValue) locals.get(i);
            if (!sv.isLocation()) continue;

            Location loc = ((LocationValue) sv).getLocation();
            Address addr = null;
            String regName = "";

            if (loc.isRegister()) {
                int reg = loc.getRegisterNumber();
                addr = vf.getRegisterMap().getLocation(new VMReg(reg));
                regName = ":" + VMRegImpl.getRegisterName(reg);
            } else if (loc.isStack() && !loc.isIllegal()) {
                addr = vf.getFrame().getUnextendedSP().addOffsetTo(loc.getStackOffset());
            }

            String value = getValue(addr, loc.getType());
            System.out.println("    [" + i + "] " + addr + regName + " = " + value);
        }
    }

    private void dumpInterpretedFrame(InterpretedVFrame vf) {
        Method method = vf.getMethod();
        int locals = (int) (method.isNative() ? method.getSizeOfParameters() : method.getMaxLocals());
        OopMapCacheEntry oopMask = method.getMaskFor(vf.getBCI());

        for (int i = 0; i < locals; i++) {
            Address addr = vf.getFrame().addressOfInterpreterFrameLocal(i);
            String value = getValue(addr, oopMask.isOop(i) ? Location.Type.OOP : Location.Type.NORMAL);
            System.out.println("    [" + i + "] " + addr + " = " + value);
        }
    }

    private String getValue(Address addr, Location.Type type) {
        if (type == Location.Type.INVALID || addr == null) {
            return "(invalid)";
        } else if (type == Location.Type.OOP) {
            return "(oop) " + getOopName(addr.getOopHandleAt(0));
        } else if (type == Location.Type.NARROWOOP) {
            return "(narrow_oop) " + getOopName(addr.getCompOopHandleAt(0));
        } else if (type == Location.Type.NORMAL) {
            return "(int) 0x" + Integer.toHexString(addr.getJIntAt(0));
        } else {
            return "(" + type + ") 0x" + Long.toHexString(addr.getJLongAt(0));
        }
    }

    private String getOopName(OopHandle hadle) {
        if (hadle == null) {
            return "null";
        }
        Oop oop = VM.getVM().getObjectHeap().newOop(hadle);
        return oop.getKlass().getName().asString();
    }

    public static void main(String[] args) throws Exception {
        new Frames().execute(args);
    }
}
```

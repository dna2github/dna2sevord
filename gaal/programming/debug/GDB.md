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
  public static void main(String[] args) {
    boolean test = true;
    String o = "This is a ghost";
    while (test) {
      System.out.println("Hello World");
      try { Thread.sleep(1000); } catch (Exception e) {}
    }
    System.out.println("Bye-bye");
  }
}
```

byte code:
```java
public class Test {
  public Test();
    Code:
       0: aload_0
       1: invokespecial #1                  // Method java/lang/Object."<init>":()V
       4: return

  public static void main(java.lang.String[]);
    Code:
       0: iconst_1
       1: istore_1
       2: ldc           #2                  // String This is a ghost
       4: astore_2
       5: iload_1
       6: ifeq          30
       9: getstatic     #3                  // Field java/lang/System.out:Ljava/io/PrintStream;
      12: ldc           #4                  // String Hello World
      14: invokevirtual #5                  // Method java/io/PrintStream.println:(Ljava/lang/String;)V
      17: ldc2_w        #6                  // long 1000l
      20: invokestatic  #8                  // Method java/lang/Thread.sleep:(J)V
      23: goto          5
      26: astore_3
      27: goto          5
      30: getstatic     #3                  // Field java/lang/System.out:Ljava/io/PrintStream;
      33: ldc           #10                 // String Bye-bye
      35: invokevirtual #5                  // Method java/io/PrintStream.println:(Ljava/lang/String;)V
      38: return
    Exception table:
       from    to  target type
          17    23    26   Class java/lang/Exception
}
```

Now thinking the solution. Have a progress track:

- `javac Test.java`, `javap -c Test.class` and `java -cp . Test`
- `jmap -dump:file=hex <pid> && jhat hex` and browse at http://localhost:7000;
cannot find any reference to `test` (it is not an object and just an instance of `class Z`)
- `jstack <pid>` can get the tid of main thread (0x7fa412002000)
and `jhat hex` has the object of the java.lang.Thread of main (0x76ab05c40)
- `java.lang.Thread` has a native method `start0`
which invokes hotspot method of `JVM_StartThread` (hotspot/src/share/vm/prims/jvm.cpp),
there is a class `JavaThread` may contain the memory structure for local variables in thread stack.


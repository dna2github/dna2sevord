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

Now thinking the solution. Have a progress track:

- `javac Test.java`, `javap -c Test.class` and `java -cp . Test`
- `jmap -dump:file=hex <pid> && jhat hex` and browse at http://localhost:7000;
cannot find any reference to `test` (it is not an object and just an instance of `class Z`)
- `jstack <pid>` can get the tid of main thread (0x7fa412002000)
and `jhat hex` has the object of the `java.lang.Thread` of main (0x76ab05c40)
- `java.lang.Thread` has a native method `start0`
which invokes hotspot method of `JVM_StartThread` (hotspot/src/share/vm/prims/jvm.cpp),
there is a class `JavaThread` may contain the memory structure for local variables in thread stack.


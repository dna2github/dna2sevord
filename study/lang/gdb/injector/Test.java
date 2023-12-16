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

/*
GDB Inject:
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
  > p $jvm_api[4]($jvm, $env, $jvm_args) // AttachCurrentThread
  > set $env = (long *)*$env
  > set $env_api = (long *)*$env
  > p $test_klass = $env_api[6]($env, "Test") // FindClass
  > p $test_klass_test = $env_api[144]($env, $test_klass, "test", "Z") // GetStaticFieldID
  > p $env_api[146]($env, $test_klass, $test_klass_test) // GetStaticBooleanField
  > p $env_api[155]($env, $test_klass, $test_klass_test, 0) // SetStaticBooleanField
  > p $jvm_api[5]($jvm) // DetachCurrentThread
  > c

LLDB Inject:
  > p int $r = 0
  > call (int) JNI_GetCreatedJavaVMs(0, 0, &$r)
  > p long* $jvm
  > call (int) JNI_GetCreatedJavaVMs(&$jvm, $r, &$r)
  > p long* $jvm_api = (long *)$jvm[0]
  > p long* $env
  > p long $jvm_args[3] = {0x00010008, 0, 0}
  > p ((int (*)(long*, long**, long*))($jvm_api[4]))($jvm, &$env, $jvm_args) // AttachCurrentThread
  > p long* $env_api = (long *)$env[0]
  > p long $test_klass = ((long (*)(long*, char*)) ((void*) $env_api[6]))($env, "Test") // FindClass
  > p long $test_klass_test = ((long (*)(long*, long, char*, char*)) ((void*) $env_api[144]))($env, $test_klass, "test", "Z") // GetStaticFieldID
  > p long $p = ((long (*)(long*, long, long)) ((void*) $env_api[146]))($env, $test_klass, $test_klass_test) // GetStaticBooleanField
  > p ((void (*)(long*, long, long, char)) ((void*) $env_api[155]))($env, $test_klass, $test_klass_test, 0) // SetStaticBooleanField
  > p ((int (*)(long*))($jvm_api[5]))($jvm) // DetachCurrentThread
  > c
*/

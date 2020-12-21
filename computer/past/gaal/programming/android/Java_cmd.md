# How to make Java command line utils for Android


```
# Makefile
default:
	javac -target 1.7 -source 1.7 -cp <android-sdk>/platforms/android-17/android.jar Hello.java
	<android-sdk>/build-tools/21.0.2/dx --dex --output Hello.dex Hello.class
	rm Hello.class
```

```java
// Hello.java

class Hello {
   public static void main(String[] a) {
      System.out.println("Hello world!"); 	
   }
}


// Beep.java
import android.media.MediaPlayer;

public class Beep {
    public static void main(String[] args) {
        MediaPlayer mp = new MediaPlayer();

        try {
            mp.setDataSource(args[0]);
            mp.prepare();
            mp.start();
        }
        catch (Exception e) {
        }
    }
}
```

```shell
# run script in android terminal
base=/system
export CLASSPATH=$base/framework/media_cmd.jar
exec app_process $base/bin com.android.commands.media.Media "$@"
```

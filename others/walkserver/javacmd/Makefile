default:
	echo "Make sure 'javac' and 'dx' are both available"
	echo "'javac' : java compiler"
	echo "'dx'    : class to dex tool in android sdk (sdk/build-tools/<version>/dx)"
	javac -target 1.7 -source 1.7 -cp '<sdk>/platforms/android-17/android.jar' Hello.java
	dx --dex --output Hello.dex Hello.class
	rm Hello.class
	echo "Run android command: dalvikvm -cp Hello.dex Hello"

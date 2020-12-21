# Virtual Machine over Android

> Android 6 only supports binaries with PIE enabled.

ref: (howto)[http://stackoverflow.com/questions/24818902/running-a-native-library-on-android-l-error-only-position-independent-executab]

```
CFLAGS += -fvisibility=default -fPIE
LDFLAGS += -rdynamic -fPIE -pie
```

> It is somehow difficult for root in selinux, even recently Qualcomm CPU has high-mark vulnerability.

How about build `Bochs`!

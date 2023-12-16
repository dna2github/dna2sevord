### prerequisite

rooted Android

ref: https://github.com/ChainsDD/su-binary

### prepare file disk

```
dd if=/dev/zero of=app.img count=1 bs=300MB
dd if=/dev/zero of=cache.img count=1 bs=200MB
mkfs.ext2 app.img
mkfs.ext2 cache.img
```

### prepare toolkit on Android

```
adb reboot recovery
# after enter recovery mode
adb shell
mount /system
cp /sbin/busybox /system/bin
cd /system/bin
# necessary
ln -s busybox mknod
ln -s busybox losetup
# nice to have
rm cat ls cp mount umount mv df
ln -s busybox cat
ln -s busybox ls
ln -s busybox cp
ln -s busybox mount
ln -s busybox umount
ln -s busybox mv
ln -s busybox df
```

### switch from internal to sdcard (app2sd.sh)

```
#!/bin/sh
 
# assume 3 and 4 both are free
mknod /dev/loop3 b 7 3
mknod /dev/loop4 b 7 4
losetup /dev/loop3 /sdcard/extraspace/app.img
losetup /devv/loop4 /sdcard/extraspace/cache.img
mount -o loop -t ext2 /dev/loop3 /data/app
mount -o loop -t ext2 /dev/loop4 /data/dalvik-cache
# do not forget chown to `system` instead of `root`
chown system:system /data/app
chown system:system /data/dalvik-cache
# refresh app list
PID=$(ps | grep "/system/bin/servicemanager" | grep -oE "system +[0-9]+" | grep -oE "[0-9]+")
kill -9 $PID
```

run it when ready.

### switch back

```
umount /data/app
umount /data/dalvik-cache
losetup -d /dev/loop3
losetup -d /dev/loop4
rm /dev/loop3 /dev/loop4
PID=$(ps | grep "/system/bin/servicemanager" | grep -oE "system +[0-9]+" | grep -oE "[0-9]+")
kill -9 $PID
```


# Mouse Keyboard Monitor

> ref: https://askubuntu.com/questions/1197651/ubuntu-show-what-keys-are-pressed-in-real-time

`evtest`

```
$ sudo evtest
No device specified, trying to scan all of /dev/input/event*
Available devices:
/dev/input/event0:      Power Button
/dev/input/event1:      Power Button
/dev/input/event2:      PC Speaker
/dev/input/event3:      Video Bus
/dev/input/event4:      HDA Intel HDMI HDMI/DP,pcm=3
/dev/input/event5:      HDA Intel HDMI HDMI/DP,pcm=7
/dev/input/event6:      HDA Intel HDMI HDMI/DP,pcm=8
/dev/input/event7:      HDA Intel HDMI HDMI/DP,pcm=9
/dev/input/event8:      HDA Intel HDMI HDMI/DP,pcm=10
/dev/input/event9:      HDA Intel PCH Front Mic
/dev/input/event10:     HDA Intel PCH Rear Mic
/dev/input/event11:     HDA Intel PCH Line
/dev/input/event12:     HDA Intel PCH Line Out
/dev/input/event13:     HDA Intel PCH Front Headphone
/dev/input/event14:     HDA NVidia HDMI/DP,pcm=3
/dev/input/event15:     HDA NVidia HDMI/DP,pcm=7
/dev/input/event16:     HDA NVidia HDMI/DP,pcm=8
/dev/input/event17:     ImExPS/2 Generic Explorer Mouse
/dev/input/event18:     AT Translated Set 2 keyboard
Select the device event number [0-18]:
```

```
sudo su -c 'sleep 1; timeout -k5 10 evtest --grab /dev/input/event18'
```

This command does the following:

- Waits 1 second so that you can release Return before the keyboard is grabbed (otherwise you'll get autorepeats rapidly scrolling the console)
- Starts evtest in grabbing mode on my keyboard's device file (replace it with yours).
- evtest is run with a timeout of 10 seconds, and additional grace period of 5 seconds in (unlikely) case it hangs, after which it's killed by SIGKILL, hopefully returning keyboard control to you.
- sudo is wrapped around the whole command instead of only evtest to make sure that you enter the password (if needed) before sleep 1, otherwise this sleep will be useless


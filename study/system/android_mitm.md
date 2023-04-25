```
TODO: fix self-signed cert error for Android device
```

- Android and packet receiver host (PRH) in the same WiFi.
- Android with Shadowsocks client (any proxy is okay)
- PRH with Shadowsocks server

```
pip install shadowsocks PySocks mitmproxy

edit /lib/python3.?/site-packages/shadowsocks/../socks.py
+        if (type(dest_pair[0]) == bytes): dest_pair = (dest_pair[0].decode(), dest_pair[1])
         if len(dest_pair) != 2 or dest_pair[0].startswith("["):

edit /lib/python3.?/site-packages/shadowsocks/shell.py
 def get_config(is_local):
         shortopts = 'hd:s:p:k:m:c:t:vq'
         longopts = ['help', 'fast-open', 'pid-file=', 'log-file=', 'workers=',
-                    'forbidden-ip=', 'user=', 'manager-address=', 'version']
+                    'forbidden-ip=', 'user=', 'manager-address=', 'version', "mitm="]

edit /lib/python3.?/site-packages/shadowsocks/tcprelay.py
+################################################
+import ssl
+ssl._create_default_https_context = ssl._create_unverified_context
+import socks
+import sys
+enable_mitm_proxy = "--mitm" in sys.argv
+mitm_proxy_setting = None
+if enable_mitm_proxy:
+   mitm_proxy_setting = sys.argv[sys.argv.index("--mitm") + 1]
+   mitm_proxy_parts = mitm_proxy_setting.split(":")
+   mitm_proxy_setting = (mitm_proxy_parts[0], int(mitm_proxy_parts[1]))
+   print("-- MITM proxy: ", mitm_proxy_setting)
+def socketwrap(a, b, c):
+   if mitm_proxy_setting is None:
+      return socket.socket(a, b, c)
+   s = socks.socksocket(a, b, c)
+   s.set_proxy(socks.HTTP, mitm_proxy_setting[0], mitm_proxy_setting[1])
+   return s
#!! replace socket.socket to socketwrap

mitmdump --listen-port 3128
ssserver --mitm 127.0.0.1:3128
```

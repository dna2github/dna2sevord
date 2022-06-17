redscoks -c redsocks.conf -p pid

```
base {
        // debug: connection progress
        log_debug = off;

        // info: start and end of client session
        log_info = on;

        /* possible `log' values are:
         *   stderr
         *   "file:/path/to/file"
         *   syslog:FACILITY  facility is any of "daemon", "local0"..."local7"
         */
        log = stderr;
        // log = "file:/path/to/file";
        // log = "syslog:local7";

        // detach from console
        daemon = on;

        /* Change uid, gid and root directory, these options require root
         * privilegies on startup.
         * Note, your chroot may requre /etc/localtime if you write log to syslog.
         * Log is opened before chroot & uid changing.
         * Debian, Ubuntu and some other distributions use `nogroup` instead of
         * `nobody`, so change it according to your system if you want redsocks
         * to drop root privileges.
         */
        // user = nobody;
        // group = nobody;
        // chroot = "/var/chroot";

        /* possible `redirector' values are:
         *   iptables   - for Linux
         *   ipf        - for FreeBSD
         *   pf         - for OpenBSD
         *   generic    - some generic redirector that MAY work
         */
        redirector = iptables;

        /* Override per-socket values for TCP_KEEPIDLE, TCP_KEEPCNT,
         * and TCP_KEEPINTVL. see man 7 tcp for details.
         * `redsocks' relies on SO_KEEPALIVE option heavily. */
        //tcp_keepalive_time = 0;
        //tcp_keepalive_probes = 0;
        //tcp_keepalive_intvl = 0;

        // Every `redsocks` connection needs two file descriptors for sockets.
        // If `splice` is enabled, it also needs four file descriptors for
        // pipes.  `redudp` is not accounted at the moment.  When max number of
        // connection is reached, redsocks tries to close idle connections. If
        // there are no idle connections, it stops accept()'ing new
        // connections, although kernel continues to fill listenq.

        // Set maximum number of open file descriptors (also known as `ulimit -n`).
        //  0 -- do not modify startup limit (default)
        // rlimit_nofile = 0;

        // Set maximum number of served connections. Default is to deduce safe
        // limit from `splice` setting and RLIMIT_NOFILE.
        // redsocks_conn_max = 0;

        // Close connections idle for N seconds when/if connection count
        // limit is hit.
        //  0 -- do not close idle connections
        //  7440 -- 2 hours 4 minutes, see RFC 5382 (default)
        // connpres_idle_timeout = 7440;

        // `max_accept_backoff` is a delay in milliseconds to retry `accept()`
        // after failure (e.g. due to lack of file descriptors). It's just a
        // safety net for misconfigured `redsocks_conn_max`, you should tune
        // redsocks_conn_max if accept backoff happens.
        // max_accept_backoff = 60000;
}

redsocks {
        /* `local_ip' defaults to 127.0.0.1 for security reasons,
         * use 0.0.0.0 if you want to listen on every interface.
         * `local_*' are used as port to redirect to.
         */
        local_ip = 127.0.0.1;
        local_port = 12349;

        // listen() queue length. Default value is SOMAXCONN and it should be
        // good enough for most of us.
        // listenq = 128; // SOMAXCONN equals 128 on my Linux box.

        // Enable or disable faster data pump based on splice(2) syscall.
        // Default value depends on your kernel version, true for 2.6.27.13+
        // splice = false;

        // `ip' and `port' are IP and tcp-port of proxy-server
        // You can also use hostname instead of IP, only one (random)
        // address of multihomed host will be used.
        ip = 127.0.0.1;
        port = 1080;

        // known types: socks4, socks5, http-connect, http-relay
        type = socks5;

        // login = "foobar";
        // password = "baz";

        // known ways to disclose client IP to the proxy:
        //  false -- disclose nothing
        // http-connect supports:
        //  X-Forwarded-For  -- X-Forwarded-For: IP
        //  Forwarded_ip     -- Forwarded: for=IP # see RFC7239
        //  Forwarded_ipport -- Forwarded: for="IP:port" # see RFC7239
        // disclose_src = false;

        // various ways to handle proxy failure
        //  close -- just close connection (default)
        //  forward_http_err -- forward HTTP error page from proxy as-is
        // on_proxy_fail = close;
}
```

```
# Create new chain
iptables -t nat -N REDSOCKS

# Ignore LANs and some other reserved addresses.
# See http://en.wikipedia.org/wiki/Reserved_IP_addresses#Reserved_IPv4_addresses
# and http://tools.ietf.org/html/rfc5735 for full list of reserved networks.
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 100.64.0.0/10 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN
iptables -t nat -A REDSOCKS -d 198.18.0.0/15 -j RETURN
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN

# Anything else should be redirected to port 12345
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12349

iptables -t nat -A OUTPUT -p tcp -j REDSOCKS
```

tag: command / unix-like / tcpdump

examples:

```
tcpdump -i eth0 -nn -s0 -v port 80

     -i : Select interface that the capture is to take place on,
          this will often be an ethernet card or wireless adapter but could also be a vlan or something more unusual.
          Not always required if there is only one network adapter.
    -nn : A single (n) will not resolve hostnames.
          A double (nn) will not resolve hostnames or ports.
          This is handy for not only viewing the IP / port numbers but also when capturing a large amount of data,
          as the name resolution will slow down the capture.
    -s0 : Snap length, is the size of the packet to capture.
          -s0 will set the size to unlimited - use this if you want to capture all the traffic.
          Needed if you want to pull binaries / files from network traffic.
     -v : Verbose, using (-v) or (-vv) increases the amount of detail shown in the output,
          often showing more protocol specific information.

port 80 : this is a common port filter to capture only traffic on port 80, that is of course usually HTTP.
```

```
tcpdump -A -s0 port 80

-A : have the output include the ascii strings from the capture.
     This allows easy reading and the ability to parse the output using grep or other commands.
     Another option that shows both hexadecimal output and ASCII is the -X option.
```

```
tcpdump -n icmp
tcpdump -i eth0 udp
tcpdump -i eth0 proto 17

Filter on various kinds of traffics.
Another way to specify this is to use protocol 17 that is udp.
These two commands will produce the same result.
The equivalent of the tcp filter is protocol 6.
```

```
tcpdump -i eth0 host 10.0.1.1
tcpdump -i eth0 src 10.0.1.1
tcpdump -i eth0 dst 10.0.1.1

Using the host filter will capture traffic going to (destination) and from (source) the IP address.
Alternatively capture only packets going one way using src or dst.
```

```
tcpdump -i eth0 -s0 -w test.pcap

-w : Writing a standard pcap file is a common command option.
     Writing a capture file to disk allows the file to be opened in Wireshark or other packet analysis tools.
-r : Reading a strandard pcap file.

tcpdump  -w capture-%H.pcap -G 3600 -C 200

In this command the file capture-(hour).pcap will be created every (-G) 3600 seconds (1 hour).
The files will be overwritten the following day. So you should end up with "capture-{1-24}.pcap",
if the hour was 15 the new file is "capture-15.pcap".
```

```
tcpdump -i eth0 -s0 -l port 80 | grep 'Server:'

Without the option to force line (-l) buffered (or packet buffered -C) mode
you will not always get the expected response when piping the tcpdump output to another command such as grep.
By using this option the output is sent immediately to the piped command giving an immediate response when troubleshooting.
```

```
# Capture only HTTP GET and POST packets
tcpdump -s 0 -A -vv 'tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420'
tcpdump -s 0 -A -vv 'tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504f5354'

# Show ICMP Packets that are not ECHO/REPLY (standard ping)
tcpdump 'icmp[icmptype] != icmp-echo and icmp[icmptype] != icmp-echoreply'

# Capture SMTP / POP3 Email
tcpdump -nn -l port 25 | grep -i 'MAIL FROM\|RCPT TO'

# Capture IPv6 Traffic
tcpdump -nn ip6 proto 6
tcpdump -nr ipv6-test.pcap ip6 proto 17

# Capture Start and End Packets of every non-local host
tcpdump 'tcp[tcpflags] & (tcp-syn|tcp-fin) != 0 and not src and dst net localnet'

# Capture HTTP data packets (without SYN / FIN / ACK)
tcpdump 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)'

# Top Hosts by Packets
tcpdump -nnn -t -c 200 | cut -f 1,2,3,4 -d '.' | sort | uniq -c | sort -nr | head -n 20
-c : Capture is limited by this count option

# DHCP Example
tcpdump -v -n port 67 or 68
```

> REF: https://hackertarget.com/tcpdump-examples/

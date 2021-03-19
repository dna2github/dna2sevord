# Python
3.7.x

## ctypes

`pip install libpcap`

```
import libpcap
import ctypes

pcap_if_arr = [libpcap.pcap_if() for _ in range(0, 10)]
c_pcap_if_arr = (libpcap.pcap_if * 10)(*pcap_if_arr)
c_pcap_if_pp = ctypes.POINTER(ctypes.POINTER(libpcap.pcap_if_p))(c_pcap_if_arr)

errbuf = ('\x00' * 256).encode('ascii')
c_errbuf = ctypes.c_char_p(errbuf)

ret = p.findalldevs(c_pcap_if_pp, c_errbuf)

print(c_pcap_if_pp[0][0].name) -> first NIC dev name
```

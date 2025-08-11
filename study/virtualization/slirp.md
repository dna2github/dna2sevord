# Slirp

using Claude 4 + Gemini 2.5 pro to generate a script to handle:
- stdin for packet input
- stdout for packet output
- response `ping`
- response RST for all other input
- user mode linux can use the script to handle limited requests

```python
#!/usr/bin/env python3

import time
import sys
import signal
import select
import os
import struct
import socket

def log_stderr(fd, msg):
    os.write(fd, msg.encode('utf-8', errors='replace'))

def decode_slip(data):
    """
    Decode SLIP protocol data by:
    1. Removing leading/trailing END characters (0xC0)
    2. Converting escape sequences back to original bytes

    SLIP uses:
    - END (0xC0) to frame packets
    - ESC (0xDB) followed by:
        * 0xDC to represent 0xC0 in data
        * 0xDD to represent 0xDB in data
    """
    # Split the data on END characters (0xC0) to find packet boundaries
    # Process escape sequences in the packet
    i = 1
    n = len(data) - 1
    decoded = bytearray()
    esc = False
    while i < n:
        if data[i] == 0xDB:  # ESC character
            i += 1
            if i >= n:
                esc = True
                break  # Incomplete escape at end, ignore

            if data[i] == 0xDC:  # ESC_END
                decoded.append(0xC0)
            elif data[i] == 0xDD:  # ESC_ESC
                decoded.append(0xDB)
            else:
                # Invalid escape sequence, keep as is (or could raise error)
                decoded.append(0xDB)
                decoded.append(data[i])
        else:
            decoded.append(data[i])
        i += 1

    # Output the decoded IP packet
    return bytes(decoded), esc


def parse_packet(packet_bytes):
    """
    Parse raw packet bytes to extract TCP/UDP information.
    Assumes the packet starts with an IP header.

    Returns a dictionary with packet information.
    """
    result = {}

    # Parse IP header (minimum 20 bytes)
    if len(packet_bytes) < 20:
        return {"error": "Packet too short for IP header"}

    # IP header fields
    version_ihl = packet_bytes[0]
    version = version_ihl >> 4
    ihl = (version_ihl & 0x0F) * 4  # Internet Header Length in bytes

    if version != 4:
        return {"error": f"Only IPv4 supported, got version {version}"}

    # Extract IP header fields
    result['ip_version'] = version
    result['ip_header_length'] = ihl
    result['ip_total_length'] = struct.unpack('!H', packet_bytes[2:4])[0]
    result['ip_protocol'] = packet_bytes[9]
    result['ip_source'] = socket.inet_ntoa(packet_bytes[12:16])
    result['ip_destination'] = socket.inet_ntoa(packet_bytes[16:20])

    # Skip to transport layer (TCP/UDP)
    transport_offset = ihl

    if result['ip_protocol'] == 6:  # TCP
        result['protocol'] = 'TCP'

        if len(packet_bytes) < transport_offset + 20:
            return {"error": "Packet too short for TCP header"}

        # TCP header fields
        tcp_header = packet_bytes[transport_offset:transport_offset + 20]
        result['source_port'] = struct.unpack('!H', tcp_header[0:2])[0]
        result['destination_port'] = struct.unpack('!H', tcp_header[2:4])[0]
        result['tcp_sequence'] = struct.unpack('!I', tcp_header[4:8])[0]
        result['tcp_acknowledgment'] = struct.unpack('!I', tcp_header[8:12])[0]

        # Data offset and flags
        data_offset_flags = struct.unpack('!H', tcp_header[12:14])[0]
        data_offset = (data_offset_flags >> 12) * 4
        result['tcp_header_length'] = data_offset

        # TCP flags
        flags = data_offset_flags & 0x1FF
        result['tcp_flags'] = {
            'FIN': bool(flags & 0x01),
            'SYN': bool(flags & 0x02),
            'RST': bool(flags & 0x04),
            'PSH': bool(flags & 0x08),
            'ACK': bool(flags & 0x10),
            'URG': bool(flags & 0x20),
            'ECE': bool(flags & 0x40),
            'CWR': bool(flags & 0x80),
            'NS': bool(flags & 0x100)
        }

        result['tcp_window'] = struct.unpack('!H', tcp_header[14:16])[0]
        result['tcp_checksum'] = struct.unpack('!H', tcp_header[16:18])[0]
        result['tcp_urgent_pointer'] = struct.unpack('!H', tcp_header[18:20])[0]

        # Calculate payload offset and size
        payload_offset = transport_offset + data_offset
        payload_size = result['ip_total_length'] - payload_offset
        result['payload_size'] = payload_size

    elif result['ip_protocol'] == 17:  # UDP
        result['protocol'] = 'UDP'

        if len(packet_bytes) < transport_offset + 8:
            return {"error": "Packet too short for UDP header"}

        # UDP header fields
        udp_header = packet_bytes[transport_offset:transport_offset + 8]
        result['source_port'] = struct.unpack('!H', udp_header[0:2])[0]
        result['destination_port'] = struct.unpack('!H', udp_header[2:4])[0]
        result['udp_length'] = struct.unpack('!H', udp_header[4:6])[0]
        result['udp_checksum'] = struct.unpack('!H', udp_header[6:8])[0]

        # Calculate payload size
        payload_offset = transport_offset + 8
        payload_size = result['udp_length'] - 8
        result['payload_size'] = payload_size

    else:
        result['protocol'] = f'Unknown (IP protocol {result["ip_protocol"]})'

    return result


END = b'\xc0'  # 192
ESC = b'\xdb'  # 219
ESC_END = b'\xdc' # 220
ESC_ESC = b'\xdd' # 221

def encode_slip(packet: bytes) -> bytes:
    """
    Encodes a packet of bytes into a SLIP-encoded frame.

    This function takes a bytes object, handles the necessary escaping
    of special characters (END and ESC), and wraps the result with
    END bytes.

    Args:
        packet: A bytes object representing the data to be encoded.

    Returns:
        A bytes object containing the SLIP-encoded frame.
    """
    # Using a bytearray is efficient for building the result
    encoded = bytearray()

    # Start with an END character
    encoded.extend(END)

    # Iterate through each byte of the input packet
    for byte in packet:
        if byte == END[0]:  # END[0] gets the integer value 192
            encoded.extend(ESC)
            encoded.extend(ESC_END)
        elif byte == ESC[0]: # ESC[0] gets the integer value 219
            encoded.extend(ESC)
            encoded.extend(ESC_ESC)
        else:
            encoded.append(byte)

    # End with an END character
    encoded.extend(END)

    # Return the result as an immutable bytes object
    return bytes(encoded)

def generate_drop_response(packet_bytes, drop_type='tcp_rst'):
    """
    Generate a packet to respond to any packet with a DROP result.

    Args:
        packet_bytes: Original packet bytes to respond to
        drop_type: Type of drop response
            - 'tcp_rst': TCP RST packet (for TCP packets)
            - 'icmp_port_unreachable': ICMP port unreachable (for UDP)
            - 'icmp_host_unreachable': ICMP host unreachable
            - 'icmp_admin_prohibited': ICMP administratively prohibited

    Returns:
        bytes: Response packet or None if cannot generate response
    """
    # First parse the original packet
    packet_info = parse_packet(packet_bytes)

    if 'error' in packet_info:
        return None

    icmp_ret = generate_ping_response(packet_bytes)
    if icmp_ret is not None:
        return icmp_ret
    # Determine appropriate response based on protocol
    if packet_info['protocol'] == 'TCP' and drop_type == 'tcp_rst':
        return generate_tcp_rst(packet_info, packet_bytes)
    elif packet_info['protocol'] == 'UDP' and drop_type == 'icmp_port_unreachable':
        return generate_icmp_unreachable(packet_info, packet_bytes, 3, 3)  # Port unreachable
    elif drop_type == 'icmp_host_unreachable':
        return generate_icmp_unreachable(packet_info, packet_bytes, 3, 1)  # Host unreachable
    elif drop_type == 'icmp_admin_prohibited':
        return generate_icmp_unreachable(packet_info, packet_bytes, 3, 13)  # Admin prohibited
    else:
        # Default to ICMP admin prohibited for any packet
        return generate_icmp_unreachable(packet_info, packet_bytes, 3, 13)


def generate_tcp_rst(packet_info, original_packet):
    """Generate a TCP RST packet in response to a TCP packet"""
    response = bytearray()

    # IP header (20 bytes) - swap source and destination
    response.append(0x45)  # Version 4, IHL 5
    response.append(0x00)  # Type of Service
    response.extend(struct.pack('!H', 40))  # Total length: 40 bytes (20 IP + 20 TCP)
    response.extend(struct.pack('!H', 0))   # Identification
    response.extend([0x40, 0x00])  # Don't fragment flag
    response.extend([0x40, 0x06])  # TTL 64, Protocol TCP (6)
    response.extend([0x00, 0x00])  # Checksum (placeholder)

    # Swap source and destination IPs
    response.extend(socket.inet_aton(packet_info['ip_destination']))
    response.extend(socket.inet_aton(packet_info['ip_source']))

    # Calculate IP checksum
    ip_checksum = calculate_ip_checksum(response[:20])
    response[10:12] = struct.pack('!H', ip_checksum)

    # TCP header (20 bytes)
    # Swap source and destination ports
    response.extend(struct.pack('!H', packet_info['destination_port']))
    response.extend(struct.pack('!H', packet_info['source_port']))

    # Sequence number: use acknowledgment number from original if ACK set
    if packet_info.get('tcp_flags', {}).get('ACK', False):
        seq_num = packet_info['tcp_acknowledgment']
    else:
        seq_num = 0
    response.extend(struct.pack('!I', seq_num))

    # Acknowledgment number: sequence + 1 if SYN, else sequence + payload
    if packet_info.get('tcp_flags', {}).get('SYN', False):
        ack_num = packet_info['tcp_sequence'] + 1
    else:
        # For simplicity, assume no payload in RST calculation
        ack_num = packet_info['tcp_sequence'] + packet_info.get('payload_size', 0)
    response.extend(struct.pack('!I', ack_num))

    # Data offset (5) and flags (RST + ACK)
    response.extend([0x50, 0x14])  # Data offset 5, RST+ACK flags

    # Window size, checksum, urgent pointer
    response.extend(struct.pack('!H', 0))     # Window
    response.extend([0x00, 0x00])             # Checksum (placeholder)
    response.extend(struct.pack('!H', 0))     # Urgent pointer

    # Calculate TCP checksum
    tcp_checksum = calculate_tcp_checksum(
        packet_info['ip_destination'],
        packet_info['ip_source'],
        response[20:]
    )
    response[36:38] = struct.pack('!H', tcp_checksum)

    return bytes(response)


def generate_icmp_unreachable(packet_info, original_packet, icmp_type, icmp_code):
    """Generate an ICMP unreachable message"""
    response = bytearray()

    # Calculate ICMP payload (IP header + 8 bytes of original packet)
    original_ip_header_len = packet_info['ip_header_length']
    icmp_payload = original_packet[:original_ip_header_len + 8]

    # Total packet length
    total_length = 20 + 8 + len(icmp_payload)  # IP + ICMP + payload

    # IP header (20 bytes)
    response.append(0x45)  # Version 4, IHL 5
    response.append(0x00)  # Type of Service
    response.extend(struct.pack('!H', total_length))
    response.extend(struct.pack('!H', 0))   # Identification
    response.extend([0x40, 0x00])  # Don't fragment flag
    response.extend([0x40, 0x01])  # TTL 64, Protocol ICMP (1)
    response.extend([0x00, 0x00])  # Checksum (placeholder)

    # Source IP is the original destination (we're sending the error back)
    response.extend(socket.inet_aton(packet_info['ip_destination']))
    response.extend(socket.inet_aton(packet_info['ip_source']))

    # Calculate IP checksum
    ip_checksum = calculate_ip_checksum(response[:20])
    response[10:12] = struct.pack('!H', ip_checksum)

    # ICMP header (8 bytes)
    response.append(icmp_type)  # Type (3 for destination unreachable)
    response.append(icmp_code)  # Code (varies by specific error)
    response.extend([0x00, 0x00])  # Checksum (placeholder)
    response.extend([0x00, 0x00, 0x00, 0x00])  # Unused

    # Add ICMP payload
    response.extend(icmp_payload)

    # Calculate ICMP checksum
    icmp_checksum = calculate_icmp_checksum(response[20:])
    response[22:24] = struct.pack('!H', icmp_checksum)

    return bytes(response)


def calculate_ip_checksum(header):
    """Calculate IP header checksum"""
    # Make sure checksum field is zero
    header_copy = bytearray(header)
    header_copy[10:12] = b'\x00\x00'

    # Sum all 16-bit words
    checksum = 0
    for i in range(0, len(header_copy), 2):
        word = (header_copy[i] << 8) + header_copy[i + 1]
        checksum += word

    # Add carry bits
    while checksum >> 16:
        checksum = (checksum & 0xFFFF) + (checksum >> 16)

    # One's complement
    return ~checksum & 0xFFFF


def calculate_tcp_checksum(src_ip, dst_ip, tcp_segment):
    """Calculate TCP checksum including pseudo-header"""
    # Create pseudo-header
    pseudo_header = bytearray()
    pseudo_header.extend(socket.inet_aton(src_ip))
    pseudo_header.extend(socket.inet_aton(dst_ip))
    pseudo_header.append(0x00)  # Reserved
    pseudo_header.append(0x06)  # Protocol (TCP)
    pseudo_header.extend(struct.pack('!H', len(tcp_segment)))

    # Combine pseudo-header and TCP segment
    data = pseudo_header + tcp_segment

    # Ensure checksum field is zero
    if len(tcp_segment) >= 18:
        data[len(pseudo_header) + 16:len(pseudo_header) + 18] = b'\x00\x00'

    # Calculate checksum
    return calculate_checksum(data)


def calculate_icmp_checksum(icmp_data):
    """Calculate ICMP checksum"""
    # Make sure checksum field is zero
    data = bytearray(icmp_data)
    data[2:4] = b'\x00\x00'
    return calculate_checksum(data)


def calculate_checksum(data):
    """Generic checksum calculation for TCP/ICMP"""
    # Pad with zero byte if odd length
    if len(data) % 2:
        data += b'\x00'

    # Sum all 16-bit words
    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        checksum += word

    # Add carry bits
    while checksum >> 16:
        checksum = (checksum & 0xFFFF) + (checksum >> 16)

    # One's complement
    return ~checksum & 0xFFFF


def generate_ping_response(raw_packet: bytes):
    """
    Checks if a raw packet is an ICMP Echo Request (ping) and, if so,
    generates an ICMP Echo Reply packet.

    Args:
        raw_packet: The raw network packet as a bytes object.

    Returns:
        A bytes object containing the raw ICMP Echo Reply packet if the input
        was a ping request, otherwise returns None.
    """
    # Minimum size for an IPv4 header is 20 bytes
    if len(raw_packet) < 20:
        return None

    # --- 1. Parse the IP Header ---
    # Unpack the first 20 bytes of the IP header
    # ! - network byte order
    # B - unsigned char (1 byte)
    # H - unsigned short (2 bytes)
    # s - bytes
    ip_header_format = '!BBHHHBBH4s4s'
    try:
        ip_header_tuple = struct.unpack(ip_header_format, raw_packet[:20])
    except struct.error:
        # Malformed packet that is not 20 bytes long
        return None

    ip_version_ihl = ip_header_tuple[0]
    ip_protocol = ip_header_tuple[6]
    original_src_ip = ip_header_tuple[8]
    original_dest_ip = ip_header_tuple[9]

    # Check if the protocol is ICMP (protocol number 1)
    if ip_protocol != 1:
        return None

    # Calculate IP header length (IHL field is in 4-byte words)
    ip_header_length = (ip_version_ihl & 0x0F) * 4

    if len(raw_packet) < ip_header_length + 8: # Min ICMP header is 8 bytes
        return None

    # --- 2. Parse the ICMP Packet ---
    icmp_packet = raw_packet[ip_header_length:]

    # Unpack ICMP header (type, code, checksum, identifier, sequence)
    icmp_header_format = '!BBHHH'
    icmp_header_tuple = struct.unpack(icmp_header_format, icmp_packet[:8])

    icmp_type = icmp_header_tuple[0]

    # Check if it's an ICMP Echo Request (Type 8)
    if icmp_type != 8:
        return None

    print(f"[*] Detected Ping Request from {socket.inet_ntoa(original_src_ip)} to {socket.inet_ntoa(original_dest_ip)}", file=sys.stderr)

    # Extract original ICMP identifier, sequence number, and data payload
    original_icmp_id = icmp_header_tuple[3]
    original_icmp_seq = icmp_header_tuple[4]
    icmp_payload = icmp_packet[8:]

    # --- 3. Construct the ICMP Echo Reply ---
    # Type 0, Code 0 for Echo Reply
    icmp_reply_type = 0
    icmp_reply_code = 0

    # Checksum will be calculated later, so set to 0 for now
    icmp_reply_checksum = 0

    # Create the ICMP reply header without the checksum
    icmp_reply_header = struct.pack(
        icmp_header_format,
        icmp_reply_type,
        icmp_reply_code,
        icmp_reply_checksum,
        original_icmp_id,  # Use same ID as request
        original_icmp_seq  # Use same sequence as request
    )

    # Calculate checksum for the new ICMP header and payload
    icmp_reply_checksum = calculate_checksum(icmp_reply_header + icmp_payload)

    # Re-pack the ICMP reply header with the correct checksum
    icmp_reply_header = struct.pack(
        icmp_header_format,
        icmp_reply_type,
        icmp_reply_code,
        icmp_reply_checksum,
        original_icmp_id,
        original_icmp_seq
    )

    # Final ICMP reply packet
    icmp_reply_packet = icmp_reply_header + icmp_payload

    # --- 4. Construct the IP Header for the Reply ---
    # Most fields are the same, but we swap IPs and recalculate the checksum
    ip_reply_src_ip = original_dest_ip   # Our IP is the original destination
    ip_reply_dest_ip = original_src_ip   # The destination is the original source

    # Create a temporary IP header to calculate its checksum
    ip_header_reply_no_checksum = struct.pack(
        ip_header_format,
        ip_version_ihl,        # Version and IHL
        ip_header_tuple[1],    # Differentiated Services
        len(raw_packet),       # Total Length (same as original packet)
        ip_header_tuple[3],    # Identification
        ip_header_tuple[4],    # Flags and Fragment Offset
        64,                    # Time To Live (a common value)
        ip_protocol,           # Protocol (ICMP)
        0,                     # Checksum (0 for calculation)
        ip_reply_src_ip,       # New Source IP
        ip_reply_dest_ip       # New Destination IP
    )

    ip_reply_checksum = calculate_checksum(ip_header_reply_no_checksum)

    # Create the final IP header with the correct checksum
    ip_header_reply = struct.pack(
        ip_header_format,
        ip_version_ihl,
        ip_header_tuple[1],
        len(raw_packet),
        ip_header_tuple[3],
        ip_header_tuple[4],
        64,
        ip_protocol,
        ip_reply_checksum,
        ip_reply_src_ip,
        ip_reply_dest_ip
    )

    # --- 5. Assemble the final response packet ---
    response_packet = ip_header_reply + icmp_reply_packet

    print("[*] Generated Ping Reply packet.", file=sys.stderr)
    return response_packet



class BinaryStdinMonitor:
    def __init__(self, chunk_size=8192):
        self.running = True
        self.chunk_size = chunk_size
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, self.signal_handler)  # kill
        signal.signal(signal.SIGQUIT, self.signal_handler)  # Ctrl+\

    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.running = False

    def read_binary_chunk(self, fd, chunk_size):
        """Read a chunk of binary data from file descriptor"""
        try:
            data = os.read(fd, chunk_size)
            return data
        except (OSError, IOError) as e:
            if e.errno == 9:  # Bad file descriptor
                return None
            raise
        except Exception:
            return None

    def write_to_stderr(self, data):
        """Write binary data to stderr"""
        try:
            packet, _ = decode_slip(data)
            print("packet:", packet, file=sys.stderr)
            print("info:", parse_packet(packet), file=sys.stderr)
            #sys.stderr.buffer.write(data)
            sys.stderr.buffer.flush()
            sys.stdout.buffer.write(encode_slip(generate_drop_response(packet)))
            sys.stdout.buffer.flush()
            return True
        except BrokenPipeError:
            return False
        except (OSError, IOError) as e:
            if e.errno in (32, 9):  # Broken pipe, Bad file descriptor
                return False
            raise
        except Exception:
            return False

    def run(self):
        """Main monitoring loop for binary data"""
        stdin_fd = sys.stdin.fileno()

        try:
            while self.running:
                # Check if data is available on stdin
                try:
                    ready, _, _ = select.select([stdin_fd], [], [], 0.1)
                except (OSError, IOError):
                    break  # stdin closed or error

                if ready:
                    # Read binary data in chunks
                    data = self.read_binary_chunk(stdin_fd, self.chunk_size)

                    if data is None or len(data) == 0:
                        # EOF or error - stdin closed
                        break

                    # Write directly to stderr buffer (binary safe)
                    if not self.write_to_stderr(data):
                        # Broken pipe on stderr
                        break

        except Exception as e:
            # Try to report error if stderr is still available
            try:
                error_msg = f"Error: {e}\n"
                log_stderr(2, error_msg)  # 2 is stderr file descriptor
            except:
                pass
            sys.exit(1)

        # Clean exit
        sys.exit(0)


def main():
    # Ensure stdin is in binary mode if needed
    if hasattr(sys.stdin, 'buffer'):
        log_stderr(2, 'using stdin buffer mode ...')
        stdin_source = sys.stdin.buffer
    else:
        log_stderr(2, 'using stdin text mode ...')
        stdin_source = sys.stdin

    monitor = BinaryStdinMonitor(chunk_size=8192)
    try:
        monitor.run()
    except Exception as e:
        try:
            error_msg = f"Fatal error: {e}\n"
            log_stderr(2, error_msg)
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()

```

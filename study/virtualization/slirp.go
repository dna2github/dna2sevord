package main

import (
	"bufio"
	"encoding/binary"
	"fmt"
	"io"
	"os"
)

const (
	SLIP_END     = 0xC0
	SLIP_ESC     = 0xDB
	SLIP_ESC_END = 0xDC
	SLIP_ESC_ESC = 0xDD

	// IP protocol numbers
	PROTO_ICMP = 1
	PROTO_TCP  = 6
	PROTO_UDP  = 17

	// ICMP types
	ICMP_DEST_UNREACH = 3
	ICMP_HOST_UNREACH = 1
)

// IP header structure (20 bytes minimum)
type IPHeader struct {
	VersionIHL     uint8
	TOS            uint8
	TotalLength    uint16
	ID             uint16
	FlagsFragOff   uint16
	TTL            uint8
	Protocol       uint8
	HeaderChecksum uint16
	SrcIP          [4]byte
	DstIP          [4]byte
}

// ICMP header structure
type ICMPHeader struct {
	Type     uint8
	Code     uint8
	Checksum uint16
	Unused   uint32
}

func main() {
	reader := bufio.NewReader(os.Stdin)
	writer := bufio.NewWriter(os.Stdout)
	defer writer.Flush()

	for {
		packet, err := readSLIPPacket(reader)
		if err != nil {
			if err == io.EOF {
				break
			}
			fmt.Fprintf(os.Stderr, "Error reading SLIP packet: %v\n", err)
			continue
		}

		if len(packet) == 0 {
			continue
		}

		fmt.Fprintf(os.Stderr, "Received packet of %d bytes\n", len(packet))

		// Parse IP header
		if len(packet) < 20 {
			fmt.Fprintf(os.Stderr, "Packet too small for IP header\n")
			continue
		}

		ipHeader := parseIPHeader(packet)
		fmt.Fprintf(os.Stderr, "IP packet: src=%v dst=%v proto=%d\n", 
			ipHeader.SrcIP, ipHeader.DstIP, ipHeader.Protocol)

		// Generate ICMP Host Unreachable response
		response := generateICMPHostUnreachable(ipHeader, packet)

		// Encode and send response
		encoded := encodeSLIP(response)
		_, err = writer.Write(encoded)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error writing response: %v\n", err)
			continue
		}
		writer.Flush()

		fmt.Fprintf(os.Stderr, "Sent ICMP Host Unreachable response\n")
	}
}

func readSLIPPacket(reader *bufio.Reader) ([]byte, error) {
	var packet []byte
	escaped := false

	for {
		b, err := reader.ReadByte()
		if err != nil {
			return nil, err
		}

		if escaped {
			switch b {
			case SLIP_ESC_END:
				packet = append(packet, SLIP_END)
			case SLIP_ESC_ESC:
				packet = append(packet, SLIP_ESC)
			default:
				// Invalid escape sequence, but continue
				packet = append(packet, b)
			}
			escaped = false
		} else {
			switch b {
			case SLIP_END:
				if len(packet) > 0 {
					return packet, nil
				}
				// Empty packet, continue reading
			case SLIP_ESC:
				escaped = true
			default:
				packet = append(packet, b)
			}
		}
	}
}

func encodeSLIP(data []byte) []byte {
	var encoded []byte
	
	// Start with END byte
	encoded = append(encoded, SLIP_END)

	for _, b := range data {
		switch b {
		case SLIP_END:
			encoded = append(encoded, SLIP_ESC, SLIP_ESC_END)
		case SLIP_ESC:
			encoded = append(encoded, SLIP_ESC, SLIP_ESC_ESC)
		default:
			encoded = append(encoded, b)
		}
	}

	// End with END byte
	encoded = append(encoded, SLIP_END)
	return encoded
}

func parseIPHeader(packet []byte) IPHeader {
	var header IPHeader
	header.VersionIHL = packet[0]
	header.TOS = packet[1]
	header.TotalLength = binary.BigEndian.Uint16(packet[2:4])
	header.ID = binary.BigEndian.Uint16(packet[4:6])
	header.FlagsFragOff = binary.BigEndian.Uint16(packet[6:8])
	header.TTL = packet[8]
	header.Protocol = packet[9]
	header.HeaderChecksum = binary.BigEndian.Uint16(packet[10:12])
	copy(header.SrcIP[:], packet[12:16])
	copy(header.DstIP[:], packet[16:20])
	return header
}

func generateICMPHostUnreachable(origIP IPHeader, origPacket []byte) []byte {
	// Create new IP header (swap src/dst)
	ipHeaderLen := 20
	icmpLen := 8 + 20 + 8 // ICMP header + IP header + 8 bytes of original data
	totalLen := ipHeaderLen + icmpLen

	response := make([]byte, totalLen)

	// IP Header
	response[0] = 0x45 // Version 4, Header length 5 (20 bytes)
	response[1] = 0    // TOS
	binary.BigEndian.PutUint16(response[2:4], uint16(totalLen))
	binary.BigEndian.PutUint16(response[4:6], 0) // ID
	binary.BigEndian.PutUint16(response[6:8], 0) // Flags and Fragment offset
	response[8] = 64                              // TTL
	response[9] = PROTO_ICMP                      // Protocol
	// Checksum calculated later
	copy(response[12:16], origIP.DstIP[:]) // Src IP (our IP is original dst)
	copy(response[16:20], origIP.SrcIP[:]) // Dst IP

	// Calculate IP checksum
	ipChecksum := calculateChecksum(response[:20])
	binary.BigEndian.PutUint16(response[10:12], ipChecksum)

	// ICMP Header
	icmpStart := 20
	response[icmpStart] = ICMP_DEST_UNREACH   // Type
	response[icmpStart+1] = ICMP_HOST_UNREACH // Code
	// Checksum calculated later
	binary.BigEndian.PutUint32(response[icmpStart+4:icmpStart+8], 0) // Unused

	// Copy original IP header + first 8 bytes of data
	copyLen := 28 // IP header (20) + 8 bytes
	if len(origPacket) < copyLen {
		copyLen = len(origPacket)
	}
	copy(response[icmpStart+8:], origPacket[:copyLen])

	// Calculate ICMP checksum
	icmpChecksum := calculateChecksum(response[icmpStart:])
	binary.BigEndian.PutUint16(response[icmpStart+2:icmpStart+4], icmpChecksum)

	return response
}

func calculateChecksum(data []byte) uint16 {
	var sum uint32

	// Add each 16-bit word
	for i := 0; i < len(data)-1; i += 2 {
		sum += uint32(data[i])<<8 + uint32(data[i+1])
	}

	// Add left-over byte, if any
	if len(data)%2 == 1 {
		sum += uint32(data[len(data)-1]) << 8
	}

	// Add carry bits
	for (sum >> 16) > 0 {
		sum = (sum & 0xffff) + (sum >> 16)
	}

	// One's complement
	return uint16(^sum)
}

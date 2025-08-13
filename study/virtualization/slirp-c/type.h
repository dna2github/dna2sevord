#ifndef _TYPE_H_
#define _TYPE_H_

// IP header structure
struct ip_header {
    uint8_t  version_ihl;
    uint8_t  tos;
    uint16_t total_length;
    uint16_t identification;
    uint16_t flags_fragment;
    uint8_t  ttl;
    uint8_t  protocol;
    uint16_t checksum;
    uint32_t src_addr;
    uint32_t dst_addr;
};

// ICMP header structure
struct icmp_header {
    uint8_t  type;
    uint8_t  code;
    uint16_t checksum;
    uint16_t identifier;
    uint16_t sequence;
};

// Protocol numbers
#define PROTO_ICMP 1
#define PROTO_TCP  6
#define PROTO_UDP  17

// ICMP types
#define ICMP_ECHO_REQUEST  8
#define ICMP_ECHO_REPLY    0

#endif

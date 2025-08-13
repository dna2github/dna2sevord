#ifndef _RESPONSE_H_
#define _RESPONSE_H_
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <arpa/inet.h>
//#include <sys/time.h>

#include "slip.h"
#include "util.h"
#include "type.h"
#include "ping.h"

// Parse IP packet and generate response
int parse_and_respond(unsigned char *packet, int packet_len, 
                      unsigned char *response, int *response_len) {
    
    struct ip_header *ip_hdr = (struct ip_header *)packet;
    
    // Get IP header length
    int ip_hdr_len = (ip_hdr->version_ihl & 0x0F) * 4;
    
    // Check IP version
    if ((ip_hdr->version_ihl >> 4) != 4) {
        fprintf(stderr, "Not IPv4 packet\n");
        return -1;
    }
    
    // Get protocol
    uint8_t protocol = ip_hdr->protocol;
    fprintf(stderr, "Protocol: %d\n", protocol);
    
    if (protocol == PROTO_ICMP) {
fprintf(stderr, "value: %02x, %02x\n", ICMP_ECHO_REQUEST, ICMP_ECHO_REPLY);
// /*
     *response_len = do_ping(packet, packet_len, response);
     if (*response_len == 0) {
        return -1;
     }
     return 0;
// */

        // Handle ICMP - generate ping response
        struct icmp_header *icmp_hdr = (struct icmp_header *)(packet + ip_hdr_len);
        
        if (icmp_hdr->type == ICMP_ECHO_REQUEST) {
            // Copy entire packet to response
            memcpy(response, packet, packet_len);
            //struct timeval tv;
            //gettimeofday(&tv, NULL);
            //memcpy(&response[28], &tv.tv_sec, 4);
            //memcpy(&response[32], &tv.tv_usec, 4);

            // Swap source and destination IP addresses
            struct ip_header *resp_ip_hdr = (struct ip_header *)response;
            uint32_t temp_addr = resp_ip_hdr->src_addr;
            resp_ip_hdr->src_addr = resp_ip_hdr->dst_addr;
            resp_ip_hdr->dst_addr = temp_addr;
            // Update ICMP header
            struct icmp_header *resp_icmp_hdr = (struct icmp_header *)(response + ip_hdr_len);
            resp_icmp_hdr->type = ICMP_ECHO_REPLY;
            resp_icmp_hdr->checksum = 0;
            
            // Calculate ICMP checksum
            int icmp_len = ntohs(resp_ip_hdr->total_length) - ip_hdr_len;
            resp_icmp_hdr->checksum = calculate_checksum(resp_icmp_hdr, icmp_len);
            
            // Update IP checksum
            resp_ip_hdr->checksum = 0;
            resp_ip_hdr->checksum = calculate_checksum(resp_ip_hdr, ip_hdr_len);
            
            *response_len = packet_len;
            fprintf(stderr, "Generated ICMP Echo Reply\n");
            return 0;
        }
    }
    else if (protocol == PROTO_TCP || protocol == PROTO_UDP) {
        // Generate DROP packet response
        // For simplicity, we'll create an ICMP Destination Unreachable message
        
        // IP header for ICMP response
        struct ip_header *resp_ip_hdr = (struct ip_header *)response;
        memset(response, 0, sizeof(struct ip_header) + 8 + 28); // IP + ICMP + original IP header + 8 bytes
        
        // Fill IP header
        resp_ip_hdr->version_ihl = 0x45; // IPv4, 20 bytes header
        resp_ip_hdr->tos = 0;
        resp_ip_hdr->total_length = htons(56); // 20 (IP) + 8 (ICMP) + 28 (original data)
        resp_ip_hdr->identification = 0;
        resp_ip_hdr->flags_fragment = 0;
        resp_ip_hdr->ttl = 64;
        resp_ip_hdr->protocol = PROTO_ICMP;
        resp_ip_hdr->src_addr = ip_hdr->dst_addr; // Our address
        resp_ip_hdr->dst_addr = ip_hdr->src_addr; // Sender's address
        
        // ICMP Destination Unreachable header
        struct icmp_header *resp_icmp_hdr = (struct icmp_header *)(response + 20);
        resp_icmp_hdr->type = 3; // Destination Unreachable
        resp_icmp_hdr->code = 3; // Port Unreachable
        resp_icmp_hdr->checksum = 0;
        
        // Copy original IP header + first 8 bytes of original data
        memcpy(response + 28, packet, ip_hdr_len + 8);
        
        // Calculate ICMP checksum
        resp_icmp_hdr->checksum = calculate_checksum(resp_icmp_hdr, 36);
        
        // Calculate IP checksum
        resp_ip_hdr->checksum = calculate_checksum(resp_ip_hdr, 20);
        
        *response_len = 56;
        fprintf(stderr, "Generated ICMP Destination Unreachable (DROP) for %s\n", 
               protocol == PROTO_TCP ? "TCP" : "UDP");
        return 0;
    }
    else {
        fprintf(stderr, "Unsupported protocol: %d\n", protocol);
        return -1;
    }
    
    return -1;
}
#endif

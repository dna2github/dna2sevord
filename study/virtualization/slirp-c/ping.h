#ifndef _PING_H_
#define _PING_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip_icmp.h> // Defines icmphdr
#include <arpa/inet.h>

#include "util.h"
#include "type.h"

#define ICMP_PACKET_SIZE 64
struct icmp_packet {
    struct icmphdr hdr;
    char msg[ICMP_PACKET_SIZE - sizeof(struct icmphdr)];
};

int do_ping(unsigned char* packet, unsigned int len, unsigned char* out) {
   int sockfd;
   struct sockaddr_in dest_addr;
   struct ip_header* hdr = (struct ip_header *)packet;
   int ip_hdr_len = (hdr->version_ihl & 0x0F) * 4;

   memset(&dest_addr, 0, sizeof(dest_addr));
   dest_addr.sin_family = AF_INET;
   //dest_addr.sin_addr.s_addr = htonl(hdr->dst_addr);
   dest_addr.sin_addr.s_addr = hdr->dst_addr;
   sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_ICMP);
   if (sockfd < 0) {
      char ipv4[INET_ADDRSTRLEN] = {0};
      const char* ipv4str = inet_ntop(AF_INET, &hdr->dst_addr, ipv4, sizeof(ipv4));
      fprintf(stderr, "[E] do_ping: could not create socket. -> %s\n", ipv4str);
      return 0;
   }

   struct timeval tv_out;
   tv_out.tv_sec = 10;
   tv_out.tv_usec = 0;
   if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv_out, sizeof(tv_out)) < 0) {
      close(sockfd);
      return 0;
   }

   struct icmp_packet pkt;
   memset(&pkt, 0, sizeof(pkt));
   pkt.hdr.type = ICMP_ECHO_REQUEST;
   pkt.hdr.code = 0;
   pkt.hdr.un.echo.id = getpid();
   pkt.hdr.un.echo.sequence = 1;
   for (int i = 0; i < sizeof(pkt.msg) - 1; i++) {
      pkt.msg[i] = i + '0';
   }
   pkt.hdr.checksum = calculate_checksum(&pkt, sizeof(pkt));

   struct timeval start, end;
   gettimeofday(&start, NULL);
   if (sendto(sockfd, &pkt, sizeof(pkt), 0, (struct sockaddr*)&dest_addr, sizeof(dest_addr)) <= 0) {
      close(sockfd);
      return 0;
   }

   unsigned char recv_buf[1024];
   struct sockaddr_in recv_addr;
   socklen_t addr_len = sizeof(recv_addr);
   size_t reclen = recvfrom(sockfd, recv_buf, sizeof(recv_buf), 0, (struct sockaddr*)&recv_addr, &addr_len);
   if (reclen <= 0) {
      close(sockfd);
      return 0;
   }
   close(sockfd);

   gettimeofday(&end, NULL);
   double rtt = (end.tv_sec - start.tv_sec) * 1000.0 + (end.tv_usec - start.tv_usec) / 1000.0;
   fprintf(stderr, "ping round-trip time: %.3f ms\n", rtt);
   memcpy(out, packet, len);
   hdr = (struct ip_header *)out;
   uint32_t temp_addr = hdr->src_addr;
   hdr->src_addr = hdr->dst_addr;
   hdr->dst_addr = temp_addr;
   hdr->checksum = 0;
   hdr->checksum = calculate_checksum(hdr, ip_hdr_len);

   struct icmp_packet* icmp = (struct icmp_packet*)((char *)hdr + ip_hdr_len);
   icmp->hdr.type = ICMP_ECHO_REPLY;
   icmp->hdr.checksum = 0;
   icmp->hdr.checksum = calculate_checksum(icmp, ntohs(hdr->total_length) - ip_hdr_len);
   //memcpy(out + ip_hdr_len, recv_buf, reclen);
   //return reclen + ip_hdr_len;
   return len;
}

#endif

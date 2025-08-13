#ifndef _UTIL_H_
#define _UTIL_H_
#include <stdio.h>
#include <stdlib.h>

// Calculate IP checksum
uint16_t calculate_checksum(void* block, int len) {
    uint16_t* data = block;
    uint32_t sum = 0;
    
    while (len > 1) {
        sum += *data++;
        len -= 2;
    }
    
    if (len == 1) {
        sum += *(uint8_t*)data;
    }
    
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    
    return (uint16_t)(~sum);
}

void dump_buf(unsigned char * buf, int len) {
   fprintf(stderr, "\nbuf: ");
   for (int i = len; i > 0; i--) {
      fprintf(stderr, "\\x%02x", *buf);
      buf++;
   }
   fprintf(stderr, "\n");
}

void dump_raw(unsigned char * buf, int len) {
   fwrite(buf, 1, len, stdout);
   fflush(stdout);
}

#endif

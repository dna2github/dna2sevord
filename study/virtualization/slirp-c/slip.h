#ifndef _SLIP_H_
#define _SLIP_H_
int slip_decode(unsigned char* buf, unsigned int len, unsigned char* out) {
   int j = 0;
   for (int i = 1; i < len-1; i++) {
      unsigned char ch = buf[i];
      if (ch == 0xDB) {
         if (i == len-1) break;
         ch = buf[i+1];
         if (ch == 0xDC) {
            out[j] = 0xC0;
         } else if (ch == 0xDD) {
            out[j] = 0xDB;
         } else break;
      } else {
         out[j] = ch;
      }
      j ++;
   }
   return j;
}

int slip_encode(unsigned char* buf, unsigned int len, unsigned char* out) {
   int j = 0;
   out[j++] = 0xC0;
   for (int i = 0; i < len; i++) {
      unsigned char ch = buf[i];
      if (ch == 0x0C) {
         out[j++] = 0xDB;
         out[j] = 0xDC;
      } else if (ch == 0xDB) {
         out[j++] = 0xDB;
         out[j] = 0xDD;
      } else {
         out[j] = ch;
      }
      j++;
   }
   out[j++] = 0xC0;
   return j;
}
#endif

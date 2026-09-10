#include <stdint.h>
#include <stdio.h>
int main(void){uint32_t x=0x01020304; unsigned char*b=(unsigned char*)&x; printf("first_byte=%02x\norder=%s\n",b[0],b[0]==4?"little":"big");}

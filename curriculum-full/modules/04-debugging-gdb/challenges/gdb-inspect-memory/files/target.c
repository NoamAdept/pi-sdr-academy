#include <stdint.h>
#include <stdio.h>
static void inspect_packet(const uint8_t *packet){printf("%u\n",packet[0]);}
int main(void){uint8_t packet[8]={0xaa,0x55,0x03,0x10,0x00,0xfe,0x01,0xef};inspect_packet(packet);}

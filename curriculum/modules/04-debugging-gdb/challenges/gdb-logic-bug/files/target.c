#include <stdio.h>
int main(void){int samples[]={9,10,14,20,21,17};int usable=0;for(int i=0;i<6;i++){if(samples[i]>10 || samples[i]<20){usable++;}}printf("usable=%d\n",usable);}

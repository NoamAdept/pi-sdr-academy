#include <stdio.h>
static void inspect_here(int level){volatile int visible=level;(void)visible;}
int main(void){int samples[]={3,7,-2,9,4};int level=10;for(int i=0;i<5;i++){level+=samples[i];inspect_here(level);}printf("%d\n",level);}

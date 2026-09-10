#include <stdio.h>
static int checkpoint(int sample){ return sample / 3; }
int main(void){int base=17;int shifted=(base<<2)+5;printf("%d\n",checkpoint(shifted));return 0;}

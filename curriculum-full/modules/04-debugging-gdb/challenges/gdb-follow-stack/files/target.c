#include <stdio.h>
__attribute__((noinline)) static int capture(int x){return x+1;}
__attribute__((noinline)) static int demodulate(int x){return capture(x*2);}
__attribute__((noinline)) static int receive(int x){return demodulate(x+3);}
int main(void){printf("%d\n",receive(4));return 0;}

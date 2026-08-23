#include <stdio.h>
#include <stdint.h>
static uintptr_t outer;
static void probe(int d){int local;if(d==0){printf("outer=%p deeper=%p direction=%s\n",(void*)outer,(void*)&local,(uintptr_t)&local<outer?"lower":"higher");return;}probe(d-1);}
int main(void){int x;outer=(uintptr_t)&x;probe(2);}

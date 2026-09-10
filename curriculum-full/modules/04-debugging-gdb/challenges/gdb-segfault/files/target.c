#include <stdio.h>
static int largest(const int *values, int count) {
    int best = values[0];
    for (int i = 1; i <= count; ++i) {
        if (values[i] > best) best = values[i];
    }
    return best;
}
int main(void){int values[]={4,12,7,-1};printf("largest=%d\n",largest(values,4));return 0;}

#include <stdio.h>
#include "signal.h"
int main(void) {
    int values[] = {10, 15, 20};
    printf("average=%d\n", average(values, 3));
    return 0;
}

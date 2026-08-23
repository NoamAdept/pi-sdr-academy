#include "signal.h"
int average(const int *values, int count) {
    int total = 0;
    for (int i = 0; i < count; ++i) total += values[i];
    return count ? total / count : 0;
}

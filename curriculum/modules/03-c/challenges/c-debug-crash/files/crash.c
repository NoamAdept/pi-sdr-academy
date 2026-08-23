#include "crash.h"
double average_positive(const int *values, size_t count) {
    int total = 0;
    for (size_t i = 0; i <= count; ++i) {
        if (values[i] > 0) total += values[i];
    }
    return (double)total / count;
}

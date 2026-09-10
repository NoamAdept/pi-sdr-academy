#ifndef RECORDS_H
#define RECORDS_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef void (*record_visitor)(uint8_t, const uint8_t *, size_t, void *);
bool parse_records(const uint8_t *data, size_t size, record_visitor visit, void *context);
#endif

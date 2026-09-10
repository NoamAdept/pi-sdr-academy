#ifndef LAYOUT_H
#define LAYOUT_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
struct header { char tag[2]; uint16_t sequence; uint8_t flags; uint8_t length; };
bool decode_header(const uint8_t *data, size_t size, struct header *out);
#endif

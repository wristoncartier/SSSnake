#ifndef MEMORY_H
#define MEMORY_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Memory manipulation functions
bool write_memory(void* address, const void* buffer, size_t size);
bool read_memory(void* address, void* buffer, size_t size);
void* allocate_memory(size_t size);
void free_memory(void* address);
bool protect_memory(void* address, size_t size, int protection);

// Pattern scanning
void* find_pattern(const void* start, size_t size, const char* pattern, const char* mask);

#ifdef __cplusplus
}
#endif

#endif // MEMORY_H

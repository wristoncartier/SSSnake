#include "memory.h"
#include <mach/mach.h>
#include <mach/vm_map.h>
#include <sys/mman.h>
#include <string.h>

bool write_memory(void* address, const void* buffer, size_t size) {
    vm_size_t old_protection;
    task_t task = mach_task_self();
    
    // Change memory protection to allow writing
    if (vm_protect(task, (vm_address_t)address, size,
                   FALSE, VM_PROT_READ | VM_PROT_WRITE) != KERN_SUCCESS) {
        return false;
    }
    
    // Write the data
    if (vm_write(task, (vm_address_t)address,
                 (vm_offset_t)buffer, (mach_msg_type_number_t)size) != KERN_SUCCESS) {
        return false;
    }
    
    // Restore original protection
    vm_protect(task, (vm_address_t)address, size,
              FALSE, VM_PROT_READ | VM_PROT_EXECUTE);
    
    return true;
}

bool read_memory(void* address, void* buffer, size_t size) {
    task_t task = mach_task_self();
    vm_size_t data_size = size;
    
    if (vm_read_overwrite(task, (vm_address_t)address, size,
                         (vm_address_t)buffer, &data_size) != KERN_SUCCESS) {
        return false;
    }
    
    return true;
}

void* allocate_memory(size_t size) {
    task_t task = mach_task_self();
    vm_address_t address = 0;
    
    if (vm_allocate(task, &address, size, VM_FLAGS_ANYWHERE) != KERN_SUCCESS) {
        return NULL;
    }
    
    return (void*)address;
}

void free_memory(void* address) {
    task_t task = mach_task_self();
    vm_deallocate(task, (vm_address_t)address, vm_page_size);
}

bool protect_memory(void* address, size_t size, int protection) {
    task_t task = mach_task_self();
    return vm_protect(task, (vm_address_t)address, size, FALSE, protection) == KERN_SUCCESS;
}

void* find_pattern(const void* start, size_t size, const char* pattern, const char* mask) {
    const unsigned char* data = (const unsigned char*)start;
    const unsigned char* pattern_bytes = (const unsigned char*)pattern;
    const size_t mask_length = strlen(mask);
    
    for (size_t i = 0; i <= size - mask_length; i++) {
        bool found = true;
        for (size_t j = 0; j < mask_length; j++) {
            if (mask[j] == 'x' && data[i + j] != pattern_bytes[j]) {
                found = false;
                break;
            }
        }
        if (found) {
            return (void*)(data + i);
        }
    }
    
    return NULL;
}

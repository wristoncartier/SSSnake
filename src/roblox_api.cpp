#include "roblox_api.h"
#include <mach/mach.h>
#include <mach/mach_vm.h>
#include <mach/vm_map.h>
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <syslog.h>
#include <signal.h>
#include <sys/time.h>
#include <pthread.h>
#include <unistd.h>
#include <dispatch/dispatch.h>
#include <sys/sysctl.h>
#include <libproc.h>
#include <mach-o/dyld.h>
#include <mach-o/loader.h>
#include <mach-o/nlist.h>
#include <execinfo.h>
#include <setjmp.h>

// Constants
#define MAX_PATH_LENGTH 4096
#define MAX_DYLIB_COUNT 1000
#define MAX_BACKTRACE_SIZE 64

// Forward declarations
static bool safe_read_memory(void* address, void* buffer, size_t size);
static int custom_print(lua_State* L);
static void signal_handler(int sig);

// Lua function types
typedef lua_State* (*lua_State_new)();
typedef void (*lua_close)(lua_State*);
typedef void (*lua_pushcclosure)(lua_State*, int (*fn)(lua_State*), int n);
typedef void (*lua_setglobal)(lua_State*, const char* name);
typedef int (*luaL_loadstring)(lua_State*, const char* s);
typedef int (*lua_pcall)(lua_State*, int nargs, int nresults, int errfunc);

// Global variables
static lua_State* g_lua_state = NULL;
static void* g_roblox_base = NULL;
static char g_error_buffer[1024];
static bool g_initialized = false;
static sigjmp_buf g_jmp_buf;  // For handling signals during memory scanning

// Function pointers for Lua API
static lua_State_new g_lua_newstate = NULL;
static lua_close g_lua_close = NULL;
static lua_pushcclosure g_lua_pushcclosure = NULL;
static lua_setglobal g_lua_setglobal = NULL;
static luaL_loadstring g_luaL_loadstring = NULL;
static lua_pcall g_lua_pcall = NULL;

// Signal handler
static void signal_handler(int sig) {
    void* array[MAX_BACKTRACE_SIZE];
    size_t size;
    
    // Get backtrace
    size = backtrace(array, MAX_BACKTRACE_SIZE);
    
    // Log signal and backtrace
    syslog(LOG_ERR, "Signal %d received", sig);
    backtrace_symbols_fd(array, size, STDERR_FILENO);
    
    // Jump back to the scanning loop
    siglongjmp(g_jmp_buf, 1);
}

// Logging function
static void log_error(const char* format, ...) {
    va_list args;
    va_start(args, format);
    vsnprintf(g_error_buffer, sizeof(g_error_buffer), format, args);
    va_end(args);
    syslog(LOG_ERR, "%s", g_error_buffer);
    fprintf(stderr, "Error: %s\n", g_error_buffer);
}

// Safe memory operations with timeout
static bool safe_read_memory(void* address, void* buffer, size_t size) {
    if (!address || !buffer || size == 0 || size > 1024 * 1024 * 10) {
        syslog(LOG_ERR, "Invalid parameters in safe_read_memory: address=%p, buffer=%p, size=%zu",
               address, buffer, size);
        return false;
    }
    
    // Break large reads into chunks
    size_t bytes_read = 0;
    while (bytes_read < size) {
        size_t chunk_size = size - bytes_read;
        if (chunk_size > 4096) chunk_size = 4096;
        
        dispatch_semaphore_t read_sem = dispatch_semaphore_create(0);
        if (!read_sem) {
            syslog(LOG_ERR, "Failed to create semaphore");
            return false;
        }
        
        __block bool chunk_success = false;
        __block kern_return_t kr;
        __block vm_offset_t data_ptr = 0;
        __block mach_msg_type_number_t data_size = (mach_msg_type_number_t)chunk_size;
        
        dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_HIGH, 0), ^{
            kr = vm_read(mach_task_self(), 
                        (vm_address_t)((char*)address + bytes_read),
                        chunk_size, 
                        &data_ptr, 
                        &data_size);
            if (kr == KERN_SUCCESS) {
                memcpy((char*)buffer + bytes_read, (void*)data_ptr, chunk_size);
                vm_deallocate(mach_task_self(), data_ptr, data_size);
                chunk_success = true;
            }
            dispatch_semaphore_signal(read_sem);
        });
        
        // Wait with timeout for this chunk
        dispatch_time_t timeout = dispatch_time(DISPATCH_TIME_NOW, 50 * NSEC_PER_MSEC);
        if (dispatch_semaphore_wait(read_sem, timeout) != 0) {
            syslog(LOG_WARNING, "Memory read timeout at address %p+%zu", address, bytes_read);
            dispatch_release(read_sem);
            return false;
        }
        
        dispatch_release(read_sem);
        if (!chunk_success) {
            syslog(LOG_ERR, "Failed to read memory at address %p+%zu", address, bytes_read);
            return false;
        }
        bytes_read += chunk_size;
    }
    
    return true;
}

bool init_roblox_api(int target_pid) {
    if (g_initialized) {
        syslog(LOG_WARNING, "Roblox API already initialized");
        return true;
    }
    
    // Set up signal handlers
    signal(SIGSEGV, signal_handler);
    signal(SIGBUS, signal_handler);
    signal(SIGABRT, signal_handler);
    
    syslog(LOG_INFO, "Initializing Roblox API for PID %d...", target_pid);
    
    // Get process path
    char path[PROC_PIDPATHINFO_MAXSIZE];
    if (proc_pidpath(target_pid, path, sizeof(path)) <= 0) {
        log_error("Failed to get process path");
        return false;
    }
    
    syslog(LOG_INFO, "Target process path: %s", path);
    
    // Try to load the binary as a dynamic library
    void* handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
        log_error("Failed to load binary: %s", dlerror());
        return false;
    }
    
    // Look for Lua functions
    g_lua_newstate = (lua_State_new)dlsym(handle, "lua_newstate");
    if (!g_lua_newstate) g_lua_newstate = (lua_State_new)dlsym(handle, "luaL_newstate");
    
    g_lua_close = (lua_close)dlsym(handle, "lua_close");
    g_lua_pushcclosure = (lua_pushcclosure)dlsym(handle, "lua_pushcclosure");
    g_lua_setglobal = (lua_setglobal)dlsym(handle, "lua_setglobal");
    g_luaL_loadstring = (luaL_loadstring)dlsym(handle, "luaL_loadstring");
    g_lua_pcall = (lua_pcall)dlsym(handle, "lua_pcall");
    
    // Log what we found
    syslog(LOG_INFO, "lua_newstate: %p", g_lua_newstate);
    syslog(LOG_INFO, "lua_close: %p", g_lua_close);
    syslog(LOG_INFO, "lua_pushcclosure: %p", g_lua_pushcclosure);
    syslog(LOG_INFO, "lua_setglobal: %p", g_lua_setglobal);
    syslog(LOG_INFO, "luaL_loadstring: %p", g_luaL_loadstring);
    syslog(LOG_INFO, "lua_pcall: %p", g_lua_pcall);
    
    // Check if we found all required functions
    if (g_lua_newstate && g_lua_close && g_lua_pushcclosure && 
        g_lua_setglobal && g_luaL_loadstring && g_lua_pcall) {
        
        // Try to create a Lua state
        if (sigsetjmp(g_jmp_buf, 1) == 0) {
            g_lua_state = g_lua_newstate();
            if (g_lua_state) {
                g_initialized = true;
                syslog(LOG_INFO, "Successfully initialized Lua state");
                return true;
            }
        }
    }
    
    // Clean up
    dlclose(handle);
    log_error("Failed to find all required Lua functions");
    return false;
}

void cleanup_roblox_api() {
    if (g_lua_state) {
        g_lua_close(g_lua_state);
        g_lua_state = NULL;
    }
    
    g_initialized = false;
    syslog(LOG_INFO, "Cleaned up Roblox API");
}

bool create_lua_state() {
    if (!g_initialized || !g_lua_newstate) {
        log_error("Roblox API not initialized");
        return false;
    }
    
    if (g_lua_state) {
        g_lua_close(g_lua_state);
    }
    
    g_lua_state = g_lua_newstate();
    if (!g_lua_state) {
        log_error("Failed to create Lua state");
        return false;
    }
    
    return true;
}

bool install_lua_functions() {
    if (!g_initialized || !g_lua_state) {
        log_error("Lua state not initialized");
        return false;
    }
    
    // Install print function
    g_lua_pushcclosure(g_lua_state, custom_print, 0);
    g_lua_setglobal(g_lua_state, "print");
    
    return true;
}

bool execute_lua_script(const char* script) {
    if (!g_initialized || !g_lua_state) {
        log_error("Lua state not initialized");
        return false;
    }
    
    if (g_luaL_loadstring(g_lua_state, script) != 0) {
        log_error("Failed to load Lua script");
        return false;
    }
    
    if (g_lua_pcall(g_lua_state, 0, 0, 0) != 0) {
        log_error("Failed to execute Lua script");
        return false;
    }
    
    return true;
}

static int custom_print(lua_State* L) {
    syslog(LOG_INFO, "Lua print: %s", "TODO: implement print");
    return 0;
}

#include "injector.h"
#include "roblox_api.h"
#include <dlfcn.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <syslog.h>

// Global variables
static bool g_initialized = false;

// Function to get our own PID
static pid_t get_self_pid() {
    return getpid();
}

// Function declarations
static void* init_thread(void* arg);
bool inject_into_process();
void cleanup_injector();
bool execute_script(const char* script);

// Entry point for the injected dylib
__attribute__((constructor))
static void dylib_entry() {
    if (inject_into_process()) {
        g_initialized = true;
    }
}

// Initialization thread
static void* init_thread(void*) {
    syslog(LOG_INFO, "Initializing injector...");
    
    // Get our own PID
    pid_t pid = get_self_pid();
    syslog(LOG_INFO, "Current process PID: %d", pid);
    
    // Initialize Roblox API
    if (!init_roblox_api(pid)) {
        syslog(LOG_ERR, "Failed to initialize Roblox API");
        return NULL;
    }
    
    // Create Lua state
    if (!create_lua_state()) {
        syslog(LOG_ERR, "Failed to create Lua state");
        cleanup_roblox_api();
        return NULL;
    }
    
    // Install custom Lua functions
    if (!install_lua_functions()) {
        syslog(LOG_ERR, "Failed to install Lua functions");
        cleanup_roblox_api();
        return NULL;
    }
    
    syslog(LOG_INFO, "Injector initialized successfully");
    return (void*)1;
}

bool inject_into_process() {
    pthread_t thread;
    if (pthread_create(&thread, NULL, init_thread, NULL) != 0) {
        syslog(LOG_ERR, "Failed to create initialization thread");
        return false;
    }
    
    void* result;
    pthread_join(thread, &result);
    return result != NULL;
}

void cleanup_injector() {
    cleanup_roblox_api();
}

bool execute_script(const char* script) {
    return execute_lua_script(script);
}

// Cleanup when unloading
__attribute__((destructor))
static void dylib_cleanup() {
    if (g_initialized) {
        cleanup_injector();
        g_initialized = false;
    }
}

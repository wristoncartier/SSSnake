#ifndef ROBLOX_INJECTOR_H
#define ROBLOX_INJECTOR_H

// Define the export macro for different platforms
#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Set target process ID
EXPORT bool set_target_process(int pid);

// Inject into process
EXPORT bool inject_into_process();

// Execute script
EXPORT bool execute_script(const char* script);

// Cleanup injector
EXPORT void cleanup_injector();

// Get log messages
EXPORT const char* get_last_log_message();

// Check if injected
EXPORT bool is_injected();

#ifdef __cplusplus
}
#endif

#endif // ROBLOX_INJECTOR_H

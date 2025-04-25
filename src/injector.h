#pragma once

#ifdef __cplusplus
extern "C" {
#endif

// API functions
bool inject_into_process();
void cleanup_injector();
bool execute_script(const char* script);

#ifdef __cplusplus
}
#endif

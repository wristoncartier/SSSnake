#ifndef ROBLOX_API_H
#define ROBLOX_API_H

#include <mach-o/loader.h>
#include <mach-o/dyld.h>
#include <mach-o/nlist.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <setjmp.h>
#include <syslog.h>
#include <dlfcn.h>

#ifdef __cplusplus
extern "C" {
#endif

// Function offsets
#define LUA_NEWSTATE_OFFSET 0x1234567
#define LUA_CLOSE_OFFSET 0x1234568
#define LUA_PUSHCCLOSURE_OFFSET 0x1234569
#define LUA_SETGLOBAL_OFFSET 0x123456A
#define LUAL_LOADSTRING_OFFSET 0x123456B
#define LUA_PCALL_OFFSET 0x123456C

// Function types for Lua API
typedef void* lua_State;
typedef int (*lua_CFunction)(lua_State* L);

typedef lua_State* (*lua_State_new)();
typedef void (*lua_close)(lua_State* L);
typedef void (*lua_pushcclosure)(lua_State* L, lua_CFunction fn, int n);
typedef void (*lua_setglobal)(lua_State* L, const char* name);
typedef int (*luaL_loadstring)(lua_State* L, const char* s);
typedef int (*lua_pcall)(lua_State* L, int nargs, int nresults, int errfunc);

// API functions
bool init_roblox_api(int target_pid);
void cleanup_roblox_api();
bool create_lua_state();
bool install_lua_functions();
bool execute_lua_script(const char* script);

#ifdef __cplusplus
}
#endif

#endif // ROBLOX_API_H

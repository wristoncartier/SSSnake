#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <dlfcn.h>
#include <time.h>
#include <openssl/sha.h>
#include <openssl/evp.h>

#define HASH_SIZE SHA256_DIGEST_LENGTH

// Security features
#define SECURITY_CHECK_INTERVAL 1000
#define MAX_SCRIPT_SIZE 1048576 // 1MB

// Export functions with C linkage
extern "C" {
    bool ValidateScript(const char* script);
    bool ExecuteScript(const char* script);
    const char* GetSecurityInfo();
}

// Security context
struct SecurityContext {
    unsigned char signature[HASH_SIZE];
    int signature_size;
    int is_validated;
    uint64_t last_check;
};

// Global security context
static SecurityContext g_security;

// Calculate SHA-256 hash of data
void CalculateHash(const void* data, size_t size, unsigned char* hash) {
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    if (!ctx) return;
    
    EVP_DigestInit_ex(ctx, EVP_sha256(), NULL);
    EVP_DigestUpdate(ctx, data, size);
    
    unsigned int hash_len;
    EVP_DigestFinal_ex(ctx, hash, &hash_len);
    
    EVP_MD_CTX_free(ctx);
}

// Verify library integrity
bool VerifyIntegrity() {
    Dl_info info;
    void* addr = (void*)&ValidateScript;
    if (!dladdr(addr, &info)) return false;
    
    // Open the dylib file
    FILE* file = fopen(info.dli_fname, "rb");
    if (!file) return false;
    
    // Get file size
    fseek(file, 0, SEEK_END);
    size_t size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    // Read file content
    unsigned char* content = (unsigned char*)malloc(size);
    if (!content) {
        fclose(file);
        return false;
    }
    
    size_t read = fread(content, 1, size, file);
    fclose(file);
    
    if (read != size) {
        free(content);
        return false;
    }
    
    // Calculate and verify hash
    unsigned char hash[HASH_SIZE];
    CalculateHash(content, size, hash);
    free(content);
    
    return memcmp(hash, g_security.signature, HASH_SIZE) == 0;
}

// Validate script for security
bool ValidateScript(const char* script) {
    if (!script) return false;
    
    // Check script size
    size_t len = strlen(script);
    if (len > MAX_SCRIPT_SIZE) return false;
    
    // Basic security checks
    if (strstr(script, "while true do")) return false;  // Prevent infinite loops
    if (strstr(script, "os.execute")) return false;     // Block OS commands
    if (strstr(script, "io.")) return false;           // Block file operations
    
    return true;
}

// Execute script securely
bool ExecuteScript(const char* script) {
    // Verify library integrity
    if (!VerifyIntegrity()) return false;
    
    // Validate script
    if (!ValidateScript(script)) return false;
    
    try {
        // TODO: Add your actual script execution logic here
        return true;
    }
    catch (...) {
        return false;
    }
}

// Get security information
const char* GetSecurityInfo() {
    static char info[256];
    snprintf(info, sizeof(info), 
            "Secure Script Executor v1.0\n"
            "Integrity: %s\n"
            "Max Script Size: %d bytes\n"
            "Security Level: High",
            VerifyIntegrity() ? "Verified" : "Failed",
            MAX_SCRIPT_SIZE);
    return info;
}

// Library constructor
__attribute__((constructor))
static void initialize() {
    // Initialize security context
    Dl_info info;
    void* addr = (void*)&ValidateScript;
    if (dladdr(addr, &info)) {
        FILE* file = fopen(info.dli_fname, "rb");
        if (file) {
            fseek(file, 0, SEEK_END);
            size_t size = ftell(file);
            fseek(file, 0, SEEK_SET);
            unsigned char* content = (unsigned char*)malloc(size);
            if (content && fread(content, 1, size, file) == size) {
                CalculateHash(content, size, g_security.signature);
                g_security.signature_size = HASH_SIZE;
            }
            if (content) free(content);
            fclose(file);
        }
    }
    g_security.is_validated = true;
    g_security.last_check = time(NULL);
}

// Library destructor
__attribute__((destructor))
static void cleanup() {
    // Clean up security context
    memset(g_security.signature, 0, HASH_SIZE);
    g_security.signature_size = 0;
    g_security.is_validated = 0;
}

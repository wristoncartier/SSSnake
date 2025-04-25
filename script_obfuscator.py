import random
import string
import re

class ScriptObfuscator:
    def __init__(self):
        self.variable_map = {}
        self.string_map = {}
        
    def _generate_random_name(self, length=8):
        """Generate a random variable name"""
        chars = string.ascii_letters
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _obfuscate_strings(self, script):
        """Obfuscate string literals"""
        # Find all string literals
        strings = re.findall(r'"([^"]*)"', script)
        
        # Replace each string with an encoded version
        for s in strings:
            if s not in self.string_map:
                # Convert string to bytes and encode in base64-like format
                encoded = ''.join(f'\\{ord(c)}' for c in s)
                var_name = self._generate_random_name()
                self.string_map[s] = var_name
            
            # Replace the string with its variable
            script = script.replace(f'"{s}"', 
                f'(function() local {self.string_map[s]}="";for i=1,#{encoded} do '
                f'{self.string_map[s]}={self.string_map[s]}..string.char({encoded}:byte(i)) end; '
                f'return {self.string_map[s]} end)()')
        
        return script
    
    def _obfuscate_variables(self, script):
        """Obfuscate variable names"""
        # Find all variable declarations
        vars = re.findall(r'\blocal\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', script)
        
        # Replace each variable with an obfuscated name
        for var in vars:
            if var not in self.variable_map:
                self.variable_map[var] = self._generate_random_name()
            script = re.sub(r'\b' + var + r'\b', self.variable_map[var], script)
        
        return script
    
    def _add_junk_code(self, script):
        """Add junk code to make the script harder to read"""
        junk = [
            'do local _ = 1 end;',
            'if false then print("") end;',
            'while false do break end;',
            'repeat break until true;'
        ]
        
        # Insert junk code at random positions
        lines = script.split('\n')
        for i in range(len(lines)):
            if random.random() < 0.3:  # 30% chance to add junk
                lines[i] = random.choice(junk) + ' ' + lines[i]
        
        return '\n'.join(lines)
    
    def obfuscate(self, script):
        """Obfuscate a Lua script"""
        # Reset maps for new script
        self.variable_map.clear()
        self.string_map.clear()
        
        # Apply obfuscation techniques
        script = self._obfuscate_strings(script)
        script = self._obfuscate_variables(script)
        script = self._add_junk_code(script)
        
        # Wrap in a protected call
        script = f'''
(function()
    {script}
end)()
'''
        return script

import subprocess
import json
import sys
import shutil

class GeminiAgent:
    def __init__(self, model: str = "gemini-3-flash-preview"):
        self.model = model
        self.cli_path = shutil.which("gemini")
        
        if not self.cli_path:
            # Fallback: try to find it in common locations or suggest installation
            # For now, we assume it's in the path as per instructions
            print("Warning: 'gemini' executable not found in PATH.", file=sys.stderr)

    def run(self, query: str) -> dict:
        """
        Executes a query using the Gemini CLI in headless mode.
        """
        prompt = self._construct_prompt(query)
        
        # Build command
        cmd = [
            "gemini",
            "--prompt", prompt,
            "--model", self.model,
            "--output-format", "json"
        ]
        
        executable = self.cli_path if self.cli_path else "gemini"
        cmd[0] = executable
        
        print(f"DEBUG: Running command: {cmd}")
        
        try:
            print(f"Executing with model: {self.model}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8', 
                errors='replace',
                check=False
            )
            
            if result.returncode != 0:
                print(f"Error executing Gemini CLI: {result.stderr}", file=sys.stderr)
                # Try to salvage stdout if stderr has error but stdout has content?
                if not result.stdout:
                    return {"error": result.stderr}

            stdout = result.stdout.strip()
            
            # 1. Try direct JSON parse
            try:
                data = json.loads(stdout)
                return data
            except json.JSONDecodeError:
                pass
                
            # 2. Try to find JSON block
            import re
            json_match = re.search(r'\{.*\}', stdout, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    return data
                except json.JSONDecodeError:
                    pass
            
            # 3. Fallback: Treat as plain text response
            print("Warning: Failed to decode JSON output. Falling back to plain text.", file=sys.stderr)
            # Create a synthetic response object
            return {
                "response": stdout,
                "stats": {},
                "warning": "Parsed as plain text"
            }

        except Exception as e:
            return {"error": str(e)}

    def _construct_prompt(self, query: str) -> str:
        """
        Wraps the user query with instructions to use specific tools if necessary.
        """
        # DEBUG: Return query directly to exclude prompt issues
        return query

if __name__ == "__main__":
    # Simple test
    agent = GeminiAgent()
    print("Agent initialized.")

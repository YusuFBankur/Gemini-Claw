import os
import subprocess
import shutil
import platform
import json
from typing import Dict, Any, List, Optional

class ToolRegistry:
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)
        self.is_windows = platform.system() == "Windows"
        
        # Allowed commands whitelist
        self.allowed_commands = {
            "list_directory": self.list_directory,
            "read_file": self.read_file,
            "write_file": self.write_file,
            "make_directory": self.make_directory,
            "execute_command": self.execute_safe_command,
            "git_operation": self.git_operation
        }
        
        # Whitelist for execute_command (binary names)
        # Note: 'dir' and 'type' are shell builtins in Windows, handled carefully
        self.safe_binaries = {
            "ls", "dir", "cp", "copy", "mv", "move", "mkdir", "echo", "pwd", "whoami", "date",
            "git", "python", "python3", "cat", "type", "head", "tail", "grep", "find"
        }

    def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for tool execution."""
        if tool_name not in self.allowed_commands:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            result = self.allowed_commands[tool_name](**params)
            return {"status": "success", "output": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _validate_path(self, path: str) -> str:
        """Ensures path is within workspace."""
        # Handle relative paths
        abs_path = os.path.abspath(os.path.join(self.workspace_root, path))
        
        if not abs_path.startswith(self.workspace_root):
            raise PermissionError(f"Access denied: Path {path} is outside workspace {self.workspace_root}")
        
        return abs_path

    def list_directory(self, path: str = ".") -> str:
        target_path = self._validate_path(path)
        if not os.path.exists(target_path):
            return "Directory does not exist."
            
        items = os.listdir(target_path)
        # Add basic type info
        result = []
        for item in items:
            full_path = os.path.join(target_path, item)
            kind = "DIR" if os.path.isdir(full_path) else "FILE"
            result.append(f"[{kind}] {item}")
        return "\n".join(result)

    def read_file(self, path: str) -> str:
        target_path = self._validate_path(path)
        if not os.path.isfile(target_path):
            raise FileNotFoundError(f"File not found: {path}")
            
        # Limit size related to basic cat usage (e.g. 50KB)
        file_size = os.path.getsize(target_path)
        if file_size > 50 * 1024: 
             return f"Error: File too large to read (Size: {file_size} bytes). Max 50KB."

        with open(target_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()

    def write_file(self, path: str, content: str) -> str:
        target_path = self._validate_path(path)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"File written successfully: {path}"

    def make_directory(self, path: str) -> str:
        target_path = self._validate_path(path)
        os.makedirs(target_path, exist_ok=True)
        return f"Directory created: {path}"

    def execute_safe_command(self, command: str, args: List[str] = []) -> str:
        """Executes a system command if it's in the safe binaries list."""
        cmd_parts = command.split()
        base_cmd = cmd_parts[0] if cmd_parts else ""
        
        if base_cmd not in self.safe_binaries:
             # Check if it's a full path to a safe binary? 
             # For now, simplistic check.
             raise PermissionError(f"Command '{base_cmd}' is not in the allowlist.")

        # Construct full command for subprocess
        # NOTE: On Windows, some commands like 'dir' are shell builtins and require shell=True
        # BUT shell=True is dangerous. 
        # Better to map 'dir' to os.listdir in the agent logic, but if they insist on 'dir'...
        
        full_cmd = [command] + args
        
        # Special handling for shell builtins
        use_shell = False
        if self.is_windows and command in ["dir", "type", "echo", "copy", "move", "del"]:
             use_shell = True
        
        # Dangerous check: rm /
        full_cmd_str = " ".join(full_cmd)
        if "rm " in full_cmd_str and ("-rf" in full_cmd_str or "/" == full_cmd_str.strip()[-1]):
             raise PermissionError("Dangerous command pattern detected (rm -rf /)")

        try:
            result = subprocess.run(
                full_cmd if not use_shell else full_cmd_str,
                shell=use_shell,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]\n{result.stderr}"
            return output
        except Exception as e:
            return f"Execution Error: {str(e)}"

    def git_operation(self, subcommand: str, args: List[str] = []) -> str:
        """Specialized git wrapper."""
        if subcommand not in ["status", "log", "diff", "add", "commit", "push", "pull", "checkout", "branch", "init"]:
             raise PermissionError(f"Git subcommand '{subcommand}' not allowed/supported.")
        
        # Force non-interactive
        env = os.environ.copy()
        env["GIT_PAGER"] = "cat"
        env["GIT_TERMINAL_PROMPT"] = "0"
        
        full_cmd = ["git", subcommand] + args
        
        try:
            result = subprocess.run(
                full_cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                env=env,
                check=False
            )
            return result.stdout if result.returncode == 0 else f"Git Error:\n{result.stderr}"
        except Exception as e:
            return str(e)

import subprocess
import json
import sys
import shutil
import time
from typing import Dict, Any, Optional

class GeminiAgent:
    def __init__(self, model: str = "gemini-3-flash-preview", session_id: Optional[str] = None):
        self.model = model
        self.session_id = session_id
        self.cli_path = shutil.which("gemini")
        
        if not self.cli_path:
            import os
            npm_path = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gemini.CMD')
            if os.path.exists(npm_path):
                self.cli_path = npm_path
        
        if not self.cli_path:
            print("Warning: 'gemini' executable not found in PATH.", file=sys.stderr)

    def run(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Runs the gemini CLI and returns the parsed JSON response with telemetry."""
        if not self.cli_path:
            return {"error": "gemini-cli not found in PATH."}

        # --approval-mode yolo allows all tools to run without confirmation.
        cmd = [
            self.cli_path,
            "--model", self.model,
            "--output-format", "json",
            "--approval-mode", "yolo"
        ]
        
        if self.session_id:
            # Note: cheatsheet says -r or --resume for session ID
            # But let's check if it supports starting a new one with a name
            # Or if we should just use the default session management.
            # For now, let's stick to simple execution.
            pass
            
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nUSER REQUEST:\n{prompt}"

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                input=full_prompt,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            latency = (time.time() - start_time) * 1000
            
            if result.returncode != 0:
                stderr = result.stderr or result.stdout
                return {
                    "error": f"CLI Error (Code {result.returncode}): {stderr}",
                    "latency_ms": latency
                }

            output = result.stdout.strip()
            
            try:
                if "{" in output:
                    json_start = output.find("{")
                    json_end = output.rfind("}") + 1
                    json_str = output[json_start:json_end]
                    data = json.loads(json_str)
                    
                    if "meta" not in data:
                        data["meta"] = {}
                    data["meta"]["total_latency_ms"] = latency
                    return data
                
                return {"response": output, "meta": {"total_latency_ms": latency}}
            except json.JSONDecodeError:
                return {
                    "response": output, 
                    "warning": "Failed to decode JSON output.",
                    "meta": {"total_latency_ms": latency}
                }

        except Exception as e:
            return {"error": str(e), "latency_ms": (time.time() - start_time) * 1000}

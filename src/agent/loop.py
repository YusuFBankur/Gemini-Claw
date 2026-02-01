import time
import json
import re
from typing import Dict, Any, List, Optional
from src.agent.core import GeminiAgent
from src.agent.prompts import get_system_prompt
from src.agent.tools import ToolRegistry

class AgentLoop:
    def __init__(self, initial_model: str = "gemini-3-flash-preview", verbose: bool = False):
        self.initial_model = initial_model
        self.verbose = verbose
        # Initialize with no session ID; let the first CLI call generate one and capture it.
        self.agent = GeminiAgent(model=initial_model, session_id=None)
        self.tools = ToolRegistry(workspace_root=".") # Current directory as root
        
    def execute_with_retry(self, query: str, max_turns: int = 15) -> Dict[str, Any]:
        """
        Executes a Re-Act loop:
        1. Prompt Agent
        2. If Tool Call -> Execute -> Prompt Again (with Result)
        3. If no Tool Call -> Return Final Answer
        """
        system_prompt = get_system_prompt()
        current_query = query
        history = []
        
        start_time = time.time()
        telemetry = {"tool_calls": 0, "cli_latency_accum_ms": 0}

        turn = 0
        while turn < max_turns:
            if self.verbose:
                print(f"[DEBUG] Turn {turn+1} | Sending request...")

            # On first turn, we send system prompt. On subsequent turns, we resume session.
            sys_prompt_arg = system_prompt if turn == 0 else None
            
            # Run Agent
            result = self.agent.run(current_query, system_prompt=sys_prompt_arg)
            
            # Telemetry update
            lat = result.get("meta", {}).get("total_latency_ms", 0)
            telemetry["cli_latency_accum_ms"] += lat
            
            if "error" in result:
                return result # Propagate error immediately

            raw_response = result.get("response", "")
            
            # Try to parse Tool Call
            tool_call = self._parse_tool_call(raw_response)
            
            if tool_call:
                # ACTION DETECTED
                turn += 1
                telemetry["tool_calls"] += 1
                tool_name = tool_call.get("tool")
                params = tool_call.get("params", {})
                
                if self.verbose:
                     print(f"[DEBUG] Tool Detected: {tool_name} | Params: {params}")

                # Execute Tool
                tool_result = self.tools.execute(tool_name, params)
                
                if self.verbose:
                     print(f"[DEBUG] Tool Result: {tool_result}")

                # Format output for next turn
                # We feed the result back to the model
                current_query = f"TOOL_OUTPUT: {json.dumps(tool_result, ensure_ascii=False)}"
                
                # Check if file content is too long and truncate if needed
                if len(current_query) > 100000:
                    current_query = current_query[:100000] + "... [TRUNCATED]"
                    
            else:
                # NO ACTION -> FINAL ANSWER (or just general chat)
                total_duration = (time.time() - start_time) * 1000
                telemetry["duration_ms"] = total_duration
                
                return {
                    "raw_response": raw_response,
                    "telemetry": telemetry
                }

        return {
            "error": "Max turns reached. Agent loop terminated.",
            "telemetry": telemetry
        }

    def _parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Heuristic: Look for a JSON code block or just a raw JSON object at the start/end.
        The system prompt asks for ONLY JSON, but let's be robust.
        """
        text = text.strip()
        
        # 1. Try extracting Markdown JSON block
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
                
        # 2. Try parsing the whole text if it looks like JSON
        if text.startswith("{") and text.endswith("}"):
            try:
                return json.loads(text)
            except:
                pass
        
        return None

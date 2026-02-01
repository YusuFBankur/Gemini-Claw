import time
from typing import Dict, Any, List, Optional
from src.agent.core import GeminiAgent

class AgentLoop:
    def __init__(self, initial_model: str = "gemini-3-flash-preview", verbose: bool = False):
        self.initial_model = initial_model
        self.verbose = verbose
        # We start with a fresh session per loop execution (or could persist across calls if needed)
        self.agent = GeminiAgent(model=initial_model, session_id=f"session_{int(time.time())}")
        
    def execute_with_retry(self, query: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Executes the query using a single-shot autonomous research strategy.
        Gemini is tasked to decompose, search, fetch, and synthesize internally.
        """
        current_date = time.strftime("%Y-%m-%d")
        research_system_prompt = (
            f"You are an elite AI Research Analyst. Today's date is {current_date}.\n"
            "Your goal is to provide a comprehensive, deeply researched, and evidence-based report in Korean.\n\n"
            "RESEARCH GUIDELINES:\n"
            "1. **Recent News Focus**: Look for the most recent updates (Jan/Feb 2026). "
            "Specifically investigate investments, conflicts, and collaborations between OpenAI, Nvidia, and Amazon.\n"
            "2. **Diverse Sources**: Use `google_web_search` multiple times. "
            "Include community insights from Reddit and Hacker News for ground-level sentiments.\n"
            "3. **Deep Reading**: For high-value articles, use `web_fetch` to read the full content. "
            "Do not rely solely on search snippets.\n"
            "4. **Synthesis**: Focus on technical details, executive movements, and critical evaluations (e.g., 'AI bubble' debate).\n"
            "5. **Output**: Format the final report beautifully using Markdown. Include a 'Sources' section with URLs.\n"
            "6. **Language**: Respond in Korean, but maintain technical terms and URLs in English where appropriate."
        )

        attempts = 0
        while attempts < max_retries:
            if self.verbose:
                print(f"\n[DEBUG] Starting Autonomous Research (Attempt {attempts + 1})")

            start_time = time.time()
            result = self.agent.run(query, system_prompt=research_system_prompt)
            duration = (time.time() - start_time) * 1000

            if "error" not in result:
                # Extract interesting metadata for the TUI
                meta = result.get("meta", {})
                stats = meta.get("stats", {}) # Built-in CLI stats if available
                
                # We return a structured format for main.py to consume
                return {
                    "raw_response": result.get("response", ""),
                    "urls": self._extract_urls(result),
                    "sub_queries": result.get("thought", []), # Sometimes 'thought' contains decomposition
                    "telemetry": {
                        "duration_ms": duration,
                        "cli_latency_ms": meta.get("total_latency_ms", 0),
                        "tool_calls": result.get("meta", {}).get("tools", {}).get("totalCalls", 0)
                    }
                }

            if self.verbose:
                print(f"[DEBUG] Attempt {attempts +1} failed: {result.get('error')}")
            
            attempts += 1
            if attempts < max_retries:
                time.sleep(1) # Backoff
                
        return {"error": "Maximum retries reached during autonomous research."}

    def _extract_urls(self, result: Dict[str, Any]) -> List[str]:
        """Attempts to find URLs in the response or tools metadata."""
        urls = []
        # Check tools metadata
        tools = result.get("meta", {}).get("tools", {}).get("byName", {})
        for name, data in tools.items():
            # This depends on how gemini-cli reports tool outputs in JSON
            # Usually it's in the 'calls' or similar if present
            pass
            
        # Fallback: Regex or the model might have put them in a dedicated field
        # For now, we trust the synthesis to include them.
        return urls

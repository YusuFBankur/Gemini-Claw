import time
from typing import Dict, Any
from src.agent.core import GeminiAgent
from src.agent.search import SearchModule
from src.agent.parallel import ParallelExecutor

class AgentLoop:
    def __init__(self, initial_model: str = "gemini-3-flash-preview"):
        self.initial_model = initial_model
        self.agent = GeminiAgent(model=initial_model)
        self.search_module = SearchModule(self.agent)
        
    def execute_with_retry(self, query: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Executes the query with a loop that handles errors and tries to self-correct.
        """
        attempts = 0
        current_model = self.initial_model
        
        while attempts < max_retries:
            print(f"\n--- Attempt {attempts + 1}/{max_retries} with model {current_model} ---")
            
            # 1. Decide if we need parallelism (Simple Heuristic for now)
            # If query asks for two distinct entities, we could split.
            # "DeepMind and OpenAI"
            if "and" in query and len(query.split()) > 5:
                # Potential split, but let's try single shot first as Gemini 3 is strong.
                pass
            
            # 2. Execute
            # We assume it's a search task based on user requirements
            try:
                result = self.search_module.search(query)
                
                # 3. Validate
                if self._validate_result(result):
                    return result
                
                print("Validation failed: Output seems empty or invalid.")
                
            except Exception as e:
                print(f"Exception during execution: {str(e)}")
            
            # 4. Self-Correct / Retry strategy
            attempts += 1
            if attempts < max_retries:
                print("Retrying...")
                # Switch model if simple fallback needed (simulate auto-selection)
                # For now we stick to the best model but maybe add more detailed prompt?
                # Or re-init agent to clear partial states if any (Gemini CLI is stateless per command usually)
                pass
                
        return {"error": "Max retries reached. Failed to get a valid response."}

    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """
        Check if the result looks good.
        """
        raw = result.get("raw_response", "")
        if not raw:
            return False
        if "error" in result.get("extracted_data", {}):
            return False
        # If we got some text and it's not a CLI error, we accept it for now.
        return True

    def run_parallel_searches(self, queries: list) -> list:
        """
        Example of using the parallel executor
        """
        tasks = [lambda q=q: self.search_module.search(q) for q in queries]
        return ParallelExecutor.execute(tasks)

import time
from typing import Dict, Any
from src.agent.core import GeminiAgent
from src.agent.search import SearchModule
from src.agent.decomposition import QueryDecomposer
from src.agent.parallel import ParallelExecutor
from src.agent.fetch import FetchModule

class AgentLoop:
    def __init__(self, initial_model: str = "gemini-3-flash-preview", verbose: bool = False):
        self.initial_model = initial_model
        self.verbose = verbose
        self.agent = GeminiAgent(model=initial_model)
        self.search_module = SearchModule(self.agent)
        self.decomposer = QueryDecomposer(self.agent)
        self.fetch_module = FetchModule(self.agent)
        
    def execute_with_retry(self, query: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Executes the query with a loop that handles errors and tries to self-correct.
        """
        attempts = 0
        current_model = self.initial_model
        
        while attempts < max_retries:
            if self.verbose:
                print(f"\n--- Attempt {attempts + 1}/{max_retries} with model {current_model} ---")
            
            # 1. Decompose
            try:
                sub_queries = self.decomposer.decompose(query)
                if self.verbose:
                    print(f"Decomposed into: {sub_queries}")
                
                # 2. Parallel Search
                search_results = self.run_parallel_searches(sub_queries)
                
                # Collect URLs
                all_urls = []
                for r in search_results:
                    all_urls.extend(r.get("urls", []))
                unique_urls = list(set(all_urls))
                if self.verbose:
                    print(f"Found {len(unique_urls)} URLs. Fetching top ones for deep analysis...")
                
                # 3. Fetch Content (Deep Reading)
                # We pick top 3 distinct URLs. In a real system we'd rank them.
                # Here we trust the search order roughly.
                fetch_results = []
                if unique_urls:
                    # Batch them? or just sending one prompt with multiple URLs is supported by web_fetch logic in core?
                    # The FetchModule handles list of URLs.
                    fetch_data = self.fetch_module.fetch(unique_urls)
                    fetch_results.append(fetch_data)
                
                # 4. Synthesize
                combined_context = "\n\n".join([r.get("raw_response", "") for r in search_results])
                fetched_content = "\n\n".join([r.get("fetched_content", "") for r in fetch_results])
                
                synthesis_prompt = (
                    f"You are a Senior AI Analyst specialized in synthesizing complex technical information. "
                    f"Based on the search summaries and the DETAILED FETCHED CONTENT below, answer the user's query.\n"
                    f"**IMPORTANT**: The user asked in Korean, so you MUST answer in **Korean**.\n"
                    f"1. Provide a high-level executive summary (Korean).\n"
                    f"2. Discuss specific technical or business moves (e.g. DeepMind/OpenAI updates).\n"
                    f"3. Critically evaluate the 'bubble' question with evidence.\n"
                    f"4. Cite sources explicitly (keep URLs in English).\n\n"
                    f"User Query: {query}\n\n"
                    f"Search Context:\n{combined_context}\n\n"
                    f"Deep Read Content:\n{fetched_content}"
                )
                
                final_response = self.agent.run(synthesis_prompt)
                
                return {
                    "raw_response": final_response.get("response", ""),
                    "urls": unique_urls,
                    "sub_queries": sub_queries,
                    "fetched_data": fetch_results
                }

            except Exception as e:
                print(f"Exception during execution: {str(e)}")
            
            attempts += 1
            if attempts < max_retries:
                print("Retrying...")
                
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

from typing import List
from src.agent.core import GeminiAgent
import json
import re

class QueryDecomposer:
    def __init__(self, agent: GeminiAgent):
        self.agent = agent

    def decompose(self, query: str) -> List[str]:
        """
        Decomposes a complex query into specific, search-friendly sub-queries.
        """
        prompt = (
            f"You are an expert researcher. Break down the following user query into 3-5 specific, distinct web search queries "
            f"that will yield highly detailed and up-to-date information. "
            f"Focus on finding specific news, events, announcements, and figures mentioned (e.g., Jeff Dean, Andrej Karpathy, Ilya Sutskever). "
            f"Return the output as a JSON list of strings. \n\n"
            f"User Query: {query}\n\n"
            f"Example Output format: [\"query 1\", \"query 2\"]"
        )
        
        response = self.agent.run(prompt)
        text = response.get("response", "")
        
        # Try parse JSON
        try:
            # simple cleanup
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            queries = json.loads(text)
            if isinstance(queries, list):
                return queries
        except:
            pass
            
        # Fallback: Split by newlines or just return original
        print("Warning: Failed to parse decomposition. Using fallback.")
        return [query]

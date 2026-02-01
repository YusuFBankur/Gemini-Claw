import re
from typing import List, Dict, Any
from src.agent.core import GeminiAgent

class SearchModule:
    def __init__(self, agent: GeminiAgent):
        self.agent = agent

    def search(self, query: str) -> Dict[str, Any]:
        """
        Performs a search using the agent and extracts structured data.
        """
        # Explicit instruction for search
        prompt = (
            f"Please search for the following topic: '{query}'. "
            "Use the 'google_web_search' tool. "
            "Return the results in a JSON-like format with 'summary', 'analysis', and 'urls' (list of strings). "
            "Do not use code blocks, just raw text that looks like JSON if possible, or just clear sections."
        )
        
        response_data = self.agent.run(prompt)
        
        # If agent returned a dict with 'response', that's the text we parse
        text_response = response_data.get("response", "")
        
        urls = self._extract_urls(text_response)
        
        return {
            "query": query,
            "raw_response": text_response,
            "urls": urls,
            "extracted_data": response_data
        }

    def _extract_urls(self, text: str) -> List[str]:
        # Basic regex for URL extraction
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        # Clean up URLs (sometimes they have trailing punctuation)
        clean_urls = []
        for url in urls:
            if url.endswith('.') or url.endswith(','):
                url = url[:-1]
            clean_urls.append(url)
        return list(set(clean_urls)) # Deduplicate

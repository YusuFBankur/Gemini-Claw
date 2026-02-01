from typing import List, Dict, Any
from src.agent.core import GeminiAgent

class FetchModule:
    def __init__(self, agent: GeminiAgent):
        self.agent = agent

    def fetch(self, urls: List[str]) -> Dict[str, Any]:
        """
        Fetches content from a list of URLs using the agent's web_fetch capability.
        """
        if not urls:
            return {"error": "No URLs provided"}

        # Limit to 3 URLs to avoid overwhelming the context window or tool limits
        target_urls = urls[:3]
        url_str = ", ".join(target_urls)
        
        prompt = (
            f"Please use the 'web_fetch' tool to retrieve and read the content of the following URLs: {url_str}. "
            "Extract the full text or detailed summary from these pages. "
            "Do NOT just return the URL. I need the actual content to analyze. "
            "Return the extracted content in a structured format."
        )
        
        response = self.agent.run(prompt)
        
        return {
            "urls": target_urls,
            "fetched_content": response.get("response", ""),
            "raw_response": response
        }

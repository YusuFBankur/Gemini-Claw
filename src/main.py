import argparse
import sys
from src.agent.loop import AgentLoop

def main():
    parser = argparse.ArgumentParser(description="Gemini-Claw Agent")
    parser.add_argument("--query", type=str, required=True, help="The query to execute.")
    parser.add_argument("--model", type=str, default="gemini-3-flash-preview", help="Model to use.")
    
    args = parser.parse_args()
    
    print(f"Gemini-Claw started (Advanced Mode). Query: {args.query}")
    
    loop = AgentLoop(initial_model=args.model)
    result = loop.execute_with_retry(args.query)
    
    if "error" in result and len(result) == 1:
        print("Final Error:")
        print(result["error"])
        sys.exit(1)
        
    print("\n" + "="*50 + "\n")
    print("FINAL RESPONSE:\n")
    print(result.get("raw_response", "No response text"))
    
    urls = result.get("urls", [])
    if urls:
        print("\nExtracted URLs:")
        for url in urls:
            print(f"- {url}")
            
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()

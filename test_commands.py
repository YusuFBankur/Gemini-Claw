import sys
import os

# Ensure src is directly importable
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.agent.loop import AgentLoop

def test_command_execution():
    print(">>> Initializing Agent Loop for Test...")
    loop = AgentLoop(verbose=True)
    
    # Query designed to trigger tools (Write operation cannot be hallucinated)
    query = "Create a new directory named 'verification_test_dir' and verify it exists by listing the directory."
    
    print(f"\n>>> Running Query: '{query}'")
    result = loop.execute_with_retry(query, max_turns=5)
    
    if "error" in result:
        print(f"\n[FAIL] Error occurred: {result['error']}")
    else:
        print("\n[SUCCESS] Final Response:")
        print(result["raw_response"])
        print("\nTelemetry:", result["telemetry"])

if __name__ == "__main__":
    test_command_execution()

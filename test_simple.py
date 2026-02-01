from src.agent.core import GeminiAgent

def test():
    agent = GeminiAgent()
    print("Running simple test...")
    # Use a very simple prompt with no special instructions
    result = agent.run("What is 2+2?")
    print("Result:", result)

if __name__ == "__main__":
    test()

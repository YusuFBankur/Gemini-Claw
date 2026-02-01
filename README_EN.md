[🇰🇷 한국어](README.md) | 🇺🇸 English

# Gemini-Claw

**Gemini-Claw** is a next-generation autonomous agent platform powered by Google DeepMind's Gemini models.
Beyond a simple chatbot, it acts as an **"Autonomous Research & Synthesis Engine"** that autonomously analyzes complex research topics (Decomposition), gathers information from the web (Search & Fetch), and controls the local system (System Control) to produce results.

## 🚀 Project Vision

> "Give it a goal, and it claws its way to the answer."

Gemini-Claw aims to transform vague user requests into concrete execution plans and deliver optimal results with minimal intervention.

## ✨ Key Features

### 1. 🧠 Autonomous Research
- **Deep Research**: Conducts in-depth analysis of user queries to gather information from multiple angles.
- **Query Decomposition**: Automatically breaks down complex questions into multiple specific search queries (`src/agent/decomposition.py`) to improve information accuracy.
- **Intelligent Fetch**: Directly reads the body of searched URLs (`web_fetch`), extracting and summarizing only the necessary information.

### 2. 🛠️ Safe System Operations
The Agent safely controls the local environment via a unique Python Tool Loop (`src/agent/loop.py`).
- **File System**: Manages project structure using `ls`, `mkdir`, `read_file`, `write_file`, etc.
- **Git Integration**: Directly manages code changes via `git status`, `add`, `commit`, etc.

### 3. ⚡ Optimized Architecture
- **Parallel Execution**: Equipped with parallel processing infrastructure (`src/agent/parallel.py`) to efficiently handle multiple tasks.
- **Native Python Loop**: Implemented a lightweight and fast Python native loop instead of heavy frameworks to optimize response speed.
- **CLI Interaction**: Tightly integrated with Google's `gemini-cli` to perform at 100% capability of the latest models (Gemini 2.5/3.0).

## 📂 Project Structure

```
Gemini-Claw/
├── src/
│   ├── agent/
│   │   ├── core.py          # Gemini CLI wrapper & session management
│   │   ├── loop.py          # Main Agent Loop (Re-Act pattern implementation)
│   │   ├── tools.py         # Collection of safe system command tools
│   │   ├── search.py        # Web search module
│   │   ├── fetch.py         # Web content fetching module
│   │   └── decomposition.py # Query decomposition & analysis module
│   └── main.py              # Application entry point
├── docs/                    # Documentation (Plans & Guides)
│   └── demo/                # Demo GIFs
├── test_commands.py         # Functional verification test script
└── README.md                # Project documentation
```

## 🚀 Getting Started

### Prerequisites
This project recommends the **`uv`** package manager.
- Python 3.10+
- `gemini-cli` installation and authentication required

### Installation
```bash
git clone https://github.com/gyunggyung/Gemini-Claw.git
cd Gemini-Claw
uv sync
```

### Execution

**1. Basic Execution**
```bash
uv run python -m src.main --query "Research the latest AI trends and write a report"
```

**2. Deep Research**
```bash
uv run python -m src.main --query "Analyze latest AI industry trends: Focus on investment/conflict/collaboration between OpenAI, Nvidia, and Amazon. Also include news related to DeepMind and Anthropic. deeply cover the AI bubble theory including public opinion from Reddit or Hacker News. URLs are mandatory."
```
![Search Demo](docs/demo/Search-demo.gif)

**3. System Control (File Manipulation)**
```bash
uv run python -m src.main --query "Briefly explain all contents in the test folder, then move all contents to a newly created testmd folder. And delete the test folder."
```
![File Demo](docs/demo/File-demo.gif)

## 📜 License

This project is distributed under the [Apache License 2.0](LICENSE).

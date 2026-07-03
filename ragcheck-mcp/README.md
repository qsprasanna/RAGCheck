# RAGCheck MCP Server

An agentic skill for evaluating, diagnosing, and fixing RAG pipelines directly inside AI IDEs (Cursor, Windsurf, Claude Code).

## Capabilities & What to Expect

RAGCheck is not just a dashboard—it's an **Agentic Tool** designed to be operated by your AI coding assistant (like Cursor or Claude). You don't have to write evaluation scripts; you simply ask your AI to test your RAG pipeline, and RAGCheck handles the rest.

### 🧠 Automated Document Ingestion
Point RAGCheck at your `/docs` folder. It autonomously parses `.md`, `.txt`, and `.pdf` files, chunks the text, and builds a local SQLite vector-ready database in your workspace (`.ragcheck/ragcheck.db`) without any external vector-DB dependencies.

### 🧪 Synthetic "Golden Dataset" Generation
Instead of manually writing test questions, RAGCheck uses an LLM (defaults to cost-effective `gpt-4o-mini`) to read your ingested documents and automatically generate Question-Context-Answer (QCA) testing pairs at varying difficulty levels.

### 🕵️ Rigorous RAG Evaluation
RAGCheck runs your local chatbot/RAG script against the generated questions via your terminal. It captures the answers and uses a high-tier reasoning model (defaults to `claude-3-5-sonnet`) to score:
*   **Groundedness:** Is the chatbot hallucinating facts not present in the context?
*   **Context Recall:** Did your retriever actually find the correct chunks of text?

### 🛠️ Autonomous Code Remediation
Instead of just giving you a score, RAGCheck returns structured JSON recommendations to your AI Agent telling it exactly **how to fix your code**. For example, if Context Recall is low, it instructs Cursor to rewrite your `retriever.py` to increase the `chunk_size` or implement Hybrid Search.

---

## Installation & Configuration (BYOK)
RAGCheck is currently in Alpha and operates on a **Bring-Your-Own-Key (BYOK)** model. RAGCheck uses LiteLLM under the hood, supporting OpenAI, Anthropic, Gemini, etc.

To use the tools, you need to configure your AI IDE to connect to the RAGCheck MCP server and pass your API keys as environment variables.

### 1. Cursor
Go to **Cursor Settings > Features > MCP** and add a new server:
```json
{
  "name": "ragcheck",
  "command": "uvx",
  "args": ["git+https://github.com/qsprasanna/ragcheck-mcp.git"],
  "env": {
    "OPENAI_API_KEY": "sk-your-key-here",
    "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
  }
}
```

### 2. Claude Desktop / Claude Code
Add the following to your `claude_desktop_config.json` (usually located in `~/Library/Application Support/Claude/` on Mac):
```json
{
  "mcpServers": {
    "ragcheck": {
      "command": "uvx",
      "args": ["git+https://github.com/qsprasanna/ragcheck-mcp.git"],
      "env": {
        "OPENAI_API_KEY": "sk-your-key-here",
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```

### 3. Devin (formerly Windsurf)
In Devin, navigate to your MCP Server settings (or edit your `~/.codeium/windsurf/mcp_config.json` depending on the current version):
```json
{
  "mcpServers": {
    "ragcheck": {
      "command": "uvx",
      "args": ["git+https://github.com/qsprasanna/ragcheck-mcp.git"],
      "env": {
        "OPENAI_API_KEY": "sk-your-key-here",
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```

### 4. Codex
Depending on your Codex implementation (e.g., if using a standard MCP integration script), ensure you launch the agent with the environment variables and the `uvx` command:
```bash
OPENAI_API_KEY="sk-your-key" ANTHROPIC_API_KEY="sk-ant-key" codex --mcp "uvx git+https://github.com/qsprasanna/ragcheck-mcp.git"
```

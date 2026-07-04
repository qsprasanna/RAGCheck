# RAGCheck

An MCP (Model Context Protocol) server that evaluates, diagnoses, and fixes RAG pipelines directly inside AI IDEs — Cursor, Windsurf, Claude Code, and more.

## What It Does

RAGCheck is an **Agentic Tool** operated by your AI coding assistant. You simply ask your AI to test your RAG pipeline, and RAGCheck handles the rest:

1. **Analyze Workspace** — Parses `.md`, `.txt`, and `.pdf` files, chunks the text, and stores in a local SQLite database
2. **Generate Tests** — Uses an LLM to automatically create Question-Context-Answer (QCA) evaluation pairs from your docs
3. **Evaluate Pipeline** — Runs your RAG entrypoint against the tests and grades **Groundedness** (hallucination detection) and **Context Recall** (retrieval quality)
4. **Recommend Fixes** — Returns structured JSON telling the AI agent exactly how to fix your code

## Quick Start

### Installation (any IDE with MCP support)

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

### Usage

Ask your AI assistant:

> "Use RAGCheck to analyze my `docs/` folder, generate 5 test questions, then evaluate my pipeline with `python query.py` and fix any issues."

The agent will call the three MCP tools in sequence and apply the recommended fixes.

## BYOK — Bring Your Own Key

RAGCheck uses [LiteLLM](https://docs.litellm.ai/docs/providers) under the hood — any supported provider works:

| Provider | Env Variable | Example Model String |
|----------|-------------|---------------------|
| OpenAI | `OPENAI_API_KEY` | `gpt-4o-mini` (default for generation) |
| Anthropic | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4-6` (default for evaluation) |
| Google | `GEMINI_API_KEY` | `gemini/gemini-2.0-flash` |
| Groq | `GROQ_API_KEY` | `groq/llama-3.1-70b-versatile` |
| Ollama | (local) | `ollama/llama3` |

Pass the `model` parameter on each tool call to override the default.

## MCP Tools

| Tool | Description |
|------|-------------|
| `ragcheck_analyze_workspace` | Ingests documents from a directory and builds the evaluation baseline |
| `ragcheck_generate_tests` | Generates synthetic QCA test pairs from ingested chunks |
| `ragcheck_evaluate_pipeline` | Runs your RAG pipeline against tests and returns a health report with fix recommendations |

## IDE Setup

See [ragcheck-mcp/README.md](ragcheck-mcp/README.md) for detailed setup instructions for Cursor, Claude Desktop/Code, Devin (Windsurf), and Codex.

## Development

```bash
cd ragcheck-mcp
pip install -e .
python -m ragcheck_mcp.server
```

## License

Apache 2.0

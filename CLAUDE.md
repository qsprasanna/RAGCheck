# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAGCheck is an MCP (Model Context Protocol) server that evaluates, diagnoses, and fixes RAG pipelines from inside AI IDEs. It exposes three tools to AI agents: `ragcheck_analyze_workspace`, `ragcheck_generate_tests`, and `ragcheck_evaluate_pipeline`. The primary "user" is an AI coding agent (Claude, Cursor, etc.) acting on behalf of a developer.

## Architecture

The MCP server (`ragcheck-mcp/src/ragcheck_mcp/`) follows a pipeline:

1. **server.py** — MCP tool registration and dispatch via `mcp` library (`stdio` transport)
2. **ingestion.py** — Reads `.md`, `.txt`, `.pdf` from a docs directory, chunks text (word-based sliding window), stores in SQLite
3. **db.py** — `WorkspaceDB` class managing `.ragcheck/ragcheck.db` (tables: `documents`, `chunks`, `generated_tests`)
4. **generation.py** — Calls LiteLLM to produce QCA (Question-Context-Answer) pairs from stored chunks
5. **evaluation.py** — Runs the user's RAG entrypoint via subprocess for each test question, then uses LiteLLM to grade groundedness and context recall
6. **models.py** — Pydantic v2 models for structured JSON output (`EvaluationReport`, `MetricScore`, `FixRecommendation`)

All LLM calls go through **LiteLLM** (BYOK model). Generation defaults to `gpt-4o-mini`; evaluation defaults to `anthropic/claude-sonnet-4-6`. Any LiteLLM-supported provider works (OpenAI, Anthropic, Google, Groq, Ollama, etc.).

## Development Commands

```bash
# Install in development mode (from ragcheck-mcp/)
pip install -e .

# Run the MCP server directly
python -m ragcheck_mcp.server

# Run via uvx (as users would)
uvx git+https://github.com/qsprasanna/ragcheck-mcp.git

# Test the demo RAG pipeline
python demo/dummy_rag.py "What is the work from home policy?"
```

## Required Environment Variables (depends on chosen models)

- `OPENAI_API_KEY` — needed if using OpenAI models for generation (default: gpt-4o-mini)
- `ANTHROPIC_API_KEY` — needed if using Anthropic models for evaluation (default: anthropic/claude-sonnet-4-6)
- Other providers: set the appropriate key per LiteLLM docs (e.g., `GEMINI_API_KEY`, `GROQ_API_KEY`)

## Key Design Decisions

- The server stores all state in `.ragcheck/` within the workspace (SQLite DB + generated test JSON)
- Evaluation runs the user's RAG pipeline as a subprocess (`subprocess.run` with shell=True), passing the question as a CLI argument
- The evaluation is capped at 3 test cases per run (prototype limitation in `evaluation.py`)
- Structured JSON output via Pydantic ensures AI agents can parse responses deterministically
- Recommendations target specific files with actionable fix descriptions (not just scores)

## Demo Structure

`demo/dummy_rag.py` is an intentionally flawed RAG pipeline for testing:
- Work-from-home queries: missing the Engineering team exception (context recall failure)
- Equipment queries: hallucinated $2500 instead of the real $1000 (groundedness failure)
- Vacation queries: correct response (baseline)

`demo/docs/employee_handbook.md` contains the ground truth document.

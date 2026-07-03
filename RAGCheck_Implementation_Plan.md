# RAGCheck - Master Design Specification & Implementation Plan

## SECTION 1: Product Definition

### Mission
To provide the definitive, open-source Agentic Skill for evaluating, debugging, and certifying Retrieval-Augmented Generation (RAG) systems directly within AI coding environments. We aim to equip autonomous AI agents (like Claude Code, Antigravity) and AI IDEs (Cursor, Windsurf, GitHub Copilot) with the ability to instantly audit, diagnose, and autonomously fix RAG pipelines.

### Vision
RAGCheck envisions a future where RAG evaluation happens natively and autonomously while the developer is writing code. Instead of leaving the IDE to run complex standalone frameworks, a developer simply asks their AI assistant: *"Run a RAGCheck scan on this pipeline and fix the hallucinations."* The AI assistant uses the RAGCheck Skill (via the Model Context Protocol - MCP) to automatically generate tests, evaluate the local codebase against the vector database, pinpoint chunking or retrieval flaws, and autonomously write the code to fix them. RAGCheck will be the standard "RAG Health Skill" in every AI coding agent's toolbox.

### Goals
*   **Native AI Agent Integration**: Act as a first-class Skill via MCP for Cursor, Windsurf, Claude, and Antigravity.
*   **Autonomous Remediation**: Not just report metrics to a human, but provide structured data and exact code-diff recommendations to the host AI agent so it can rewrite the developer's chunking logic, prompts, or retrieval configuration.
*   **Zero-Setup Synthetic Testing**: Allow the agent to read the user's local documents and automatically write a golden evaluation dataset without developer intervention.
*   **Framework Agnostic**: Integrate seamlessly with LangChain, LlamaIndex, Haystack, DSPy, and custom pipelines via agent-driven code instrumentation.

### Non-goals
*   **SaaS Application Hosting**: RAGCheck is an agentic tool running locally in the developer's workspace, not a hosted SaaS dashboard platform.
*   **Standalone GUI Dashboard**: While it may output HTML reports as an artifact, the primary UX is conversational and agentic inside the IDE.
*   **General Purpose LLM Orchestration**: RAGCheck evaluates applications; it does not replace LangChain/LlamaIndex.

### Target Users & Example Personas
*   **The AI Coding Agent (Primary User)**: Claude, GPT-4, or Antigravity acting on behalf of the developer. The skill must be optimized for LLM readability, strict JSON schema outputs, and deterministic tool calls.
*   **AI Engineer (End User)**: "Cursor, use RAGCheck to check if my new sliding window chunking strategy degraded our context precision on the legal documents."
*   **Platform Engineer**: "Claude, set up an autonomous RAGCheck pre-commit hook that ensures no RAG code is pushed if groundedness drops below 95%."

---

## SECTION 2: Competitive Analysis

| Competitor | Strengths | Weaknesses | Missing Capabilities | Where RAGCheck Differentiates |
| :--- | :--- | :--- | :--- | :--- |
| **Ragas** | Good math foundations for RAG metrics; synthetic test generation. | Primarily focused on academic metrics; lacks production monitoring; slow on large datasets. | Native AI Agent/IDE integration via MCP. | RAGCheck is designed for *agents* to use natively inside the IDE to rewrite code. |
| **DeepEval** | Comprehensive metric suite; good unit-testing approach; PyTest integration. | Can be complex to set up; heavy reliance on LLM-as-a-judge which increases cost. | Autonomous remediation. | RAGCheck doesn't just fail a test; it tells the IDE agent exactly how to fix the code. |
| **TruLens** | "Feedback functions" are powerful; good dashboard for visualizations. | Instrumentation can be invasive; steep learning curve for custom apps. | Zero-setup agentic testing. | RAGCheck acts as a conversational skill, requiring no complex decorators in the source code. |
| **LangSmith** | Excellent tracing; deep integration with LangChain. | Vendor lock-in (LangChain/Smith ecosystem); expensive at scale. | Agnostic pipeline support; offline/local-only execution. | 100% open-source, local-first execution via the local AI agent. |
| **Promptfoo** | Excellent for prompt testing and assertions; very fast. | Focused on prompts/LLMs, not holistic RAG (retrieval + chunking). | Vector DB adapters; Knowledge base analysis. | RAGCheck focuses on the *entire* RAG pipeline and exposes it as an MCP tool. |

*(Note: Most competitors are building standalone SaaS or CLI tools for humans. RAGCheck is building a tool for AI Agents to use on behalf of humans.)*

---

## SECTION 3: Complete Feature List & Core Modules

RAGCheck is structured around MCP Tools exposed to the AI Agent.

### Module 1: The MCP Server (Core Engine)
*   **Tool: `ragcheck_evaluate_pipeline`**
    *   *Purpose*: Generate a one-shot health report for a RAG pipeline that an AI agent can read.
    *   *Inputs*: JSON config specifying VectorDB connection, entrypoint Python script, and test queries.
    *   *Outputs*: Structured JSON report detailing failing metrics and specific file/line targets for fixes.
*   **Tool: `ragcheck_diagnose_issue`**
    *   *Purpose*: Given a failing test case, runs deep diagnostics (bypassing the LLM to test just the retriever, or testing chunk size variations).
    *   *Outputs*: Exact code-diff suggestions to the AI agent (e.g., "Change `chunk_size` on `ingest.py:45` to 1024").

### Module 2: Agentic Document Ingestion & Analysis
*   **Tool: `ragcheck_analyze_workspace`**
    *   *Purpose*: Allows the IDE agent to parse the user's local workspace documents (`.md`, `.pdf`, `.docx`) to build the evaluation baseline.
*   **Feature: Chunk Diagnostics**
    *   *Purpose*: Identify chunks that are too small, too large, or lack semantic meaning.

### Module 3: Synthetic Test Generation
*   **Tool: `ragcheck_generate_tests`**
    *   *Purpose*: AI agent calls this tool to automatically create a golden evaluation dataset (QCA pairs) from local workspace files without user prompting.

---

## SECTION 4: Knowledge Base Analysis

Before a RAG system can be evaluated, RAGCheck must understand the underlying knowledge base to measure *coverage* and *retriever potential*.

### 1. Agent-Driven Document Ingestion
When the developer asks the agent to evaluate the RAG system, the agent invokes the `ragcheck_analyze_workspace` tool. RAGCheck employs a pluggable ingestion pipeline supporting:
*   **Text/Structured**: Markdown, HTML, CSV, JSON.
*   **PDF/Images**: Native PDFs, Scanned PDFs (via Tesseract/LayoutLM OCR).
*   **Code**: Python, TS, Go files (if building a coding RAG).

### 2. Normalization & Cleaning
*   **Deduplication**: MinHash/LSH (Locality Sensitive Hashing) to identify and remove near-duplicate documents before evaluation to prevent biased coverage scores.
*   **Metadata Extraction**: Auto-extracting author, date, domain, and document type.

### 3. Chunking Diagnostics
RAGCheck evaluates the *chunks* themselves.
*   **Strategies Analyzed**: Hierarchical, Graph, Semantic, Sliding Window.
*   **Chunk Optimization Recommendations**: RAGCheck simulates different chunk sizes (e.g., 512 vs 1024 tokens) and returns a JSON payload to the AI Agent instructing it: *"Rewrite `text_splitter.py` to use 1024 tokens with 200 token overlap."*

---

## SECTION 5: Automatic Knowledge Graph Creation

To guarantee that a RAG system can reason across documents (Multi-hop), RAGCheck builds an internal, ephemeral Knowledge Graph (KG) of the corpus in the local SQLite/DuckDB storage.

### Graph Construction Pipeline
1.  **Entity Extraction**: Using lightweight local models (GLiNER) to extract Entities.
2.  **Relationship Extraction**: Using a fast LLM to extract triplets: `(Entity A, Relationship, Entity B)`.

### Basis for Evaluation
Once the KG is built, RAGCheck uses it to:
*   **Generate Multi-hop Questions**: Find paths of length 2 or 3 in the graph to challenge the retriever.
*   **Measure Knowledge Coverage**: Calculate what percentage of the graph's nodes/edges are actually retrievable by the user's current embedding model.

---

## SECTION 6: Automatic Test Generation

RAGCheck automates the creation of a golden dataset via the `ragcheck_generate_tests` tool. 

### Generated Question Types
*   **Fact Questions**: Direct extraction from single chunks.
*   **Why/Reasoning Questions**: Requires synthesizing intent from context.
*   **Comparison Questions**: "How does Product A differ from Product B?"
*   **Multi-hop / Conversation Trees**: Follow-up questions simulating chat history.

### Pipeline Details
1.  **Generation**: LLM prompted with chunks/KG to generate Question/Context/Answer (QCA) pairs.
2.  **Deduplication**: Semantic similarity (cosine distance) to prune duplicates.
3.  **Difficulty Estimation**: Scored by the reasoning steps required (1-hop = Easy, 2-hop = Medium, Graph-traversal = Hard).

---

## SECTION 7: Multilingual Evaluation

RAGCheck treats multilingual support as a first-class citizen.

### Architecture
*   **Language Detection**: FastText or CLD3 to identify query/document languages.
*   **Translation-Free Evaluation**: Utilizing multilingual LLMs as judges to evaluate metrics natively without translating back to English.
*   **Cross-Lingual Retrieval**: Testing if a query in Hindi successfully retrieves a relevant chunk in English.

---

## SECTION 8: Evaluation Metrics

All metrics yield a score between 0.0 and 1.0, returned as strict JSON for the AI agent to parse.

### 1. Generation Metrics
*   **Groundedness (Faithfulness)**: Measures if the generated answer can be entirely deduced from the retrieved context. (The most critical metric to prevent hallucination).
*   **Answer Relevance**: Does the answer directly address the question?
*   **Citation Correctness**: Are the inline citations `[1]` pointing to the exact chunk that supports the claim?

### 2. Retrieval Metrics
*   **Context Precision**: Are the most relevant chunks ranked at the top? (Signal to the agent to adjust rerankers).
*   **Context Recall**: Did the retriever fetch all the necessary chunks to answer the question? (Signal to the agent to adjust chunk size or `top_k`).

### 3. Operational Metrics
*   **Latency**: Time to First Token (TTFT).
*   **Cost**: Calculated via tokenizer formulas.
*   **Prompt Sensitivity**: Variance in Answer Quality when the prompt is mutated slightly.

---

## SECTION 9: Hallucination Detection

RAGCheck employs a multi-layered, ensemble approach to detect hallucinations with extremely low false-positive rates.

### Detectors
1.  **LLM-as-Judge**: Prompting a frontier model with: "Given context C, does answer A contain outside information?"
2.  **NLI (Natural Language Inference)**: Using smaller, specialized local models (DeBERTa) to classify each sentence.
3.  **Graph-based**: Checking if the output asserts a relationship that explicitly contradicts the generated Knowledge Graph.

---

## SECTION 10: Retriever Evaluation & Autonomous Remediation

RAGCheck includes a dedicated diagnostic subsystem for the retriever, bypassing the LLM completely to isolate search performance.

### Comparisons Supported
*   Sparse (BM25, TF-IDF).
*   Dense (OpenAI, Cohere, BGE).
*   Hybrid Search (BM25 + Dense with Alpha tuning).
*   Rerankers (Cross-encoders).

### Autonomous Benchmarking Methodology
When the AI agent calls `ragcheck_diagnose_issue` for a Context Recall failure:
1. RAGCheck internally runs the failing questions through BM25, Dense, and Hybrid permutations.
2. It discovers that Keyword queries are failing on Dense embeddings.
3. **Recommendation Engine Payload**: RAGCheck outputs structured JSON to the IDE Agent:
   ```json
   {
     "diagnosis": "Dense retriever is failing on exact-match acronyms.",
     "recommendation_action": "enable_hybrid_search",
     "suggested_alpha": 0.3,
     "target_file": "retriever.py"
   }
   ```
4. The AI Agent reads this JSON and autonomously edits `retriever.py` for the user.

---

## SECTION 11: Prompt Evaluation & APO

Prompts degrade over time. RAGCheck secures this layer.

*   **A/B Testing**: Run Evaluation Dataset against Prompt A and Prompt B.
*   **Automatic Prompt Optimization (APO)**: Utilizing frameworks like DSPy under the hood to suggest prompt optimizations that maximize the Groundedness score. The IDE Agent can invoke `ragcheck_optimize_prompt` and immediately apply the better prompt to the user's codebase.

---

## SECTION 12: The IDE Experience & MCP Protocol

RAGCheck is architected primarily as a **Model Context Protocol (MCP)** Server.

### The Workflow Loop
1.  **User**: "Claude, make sure my new RAG bot isn't hallucinating."
2.  **Claude (IDE Agent)**: Calls `ragcheck_analyze_workspace` to read the docs.
3.  **Claude**: Calls `ragcheck_generate_tests` to build `ragcheck_tests.json`.
4.  **Claude**: Calls `ragcheck_evaluate_pipeline` targeting `main.py`.
5.  **RAGCheck**: Returns JSON: `{"health_score": 70, "failing_metric": "context_recall", "cause": "chunk_size_too_small"}`.
6.  **Claude**: Edits `main.py` to fix the chunk size.
7.  **Claude**: Calls `ragcheck_evaluate_pipeline` again.
8.  **RAGCheck**: Returns JSON: `{"health_score": 95}`.
9.  **Claude**: "I found an issue with your chunking dropping context and fixed it. Your RAG app now scores 95%."

---

## SECTION 13: CI/CD "Agentic PR Reviewer"

RAGCheck extends the agentic experience into CI/CD.

*   **Agentic PR Review**: Using GitHub Actions, a headless agent (like Antigravity) equipped with the RAGCheck MCP server evaluates every Pull Request.
*   **Autonomous Commits**: If a developer pushes a PR that drops Groundedness by 10%, the headless agent uses RAGCheck to diagnose the issue, writes a fix, and pushes a commit to the developer's PR branch automatically before merging.

---

## SECTION 14: System Architecture & Hosting Models

RAGCheck is architected to run seamlessly across different environments depending on the developer's needs, using the MCP (Model Context Protocol).

### Hosting Models

**1. Local Developer Machine (The Default - `stdio`)**
*   **How it works**: The MCP server runs directly on the developer's laptop as a subprocess of the IDE (Cursor, Windsurf) communicating via standard input/output (`stdio`).
*   **Why**: It has immediate access to local workspace files (for reading local PDFs, Python scripts), local `.env` files, and local SQLite databases. It ensures zero data exfiltration for highly secure codebases.
*   **Execution**: The developer runs `uvx ragcheck-mcp` or `npx @ragcheck/mcp` natively in their terminal or configures it in their IDE settings.

**2. Remote Enterprise Server (The Team Tier - `SSE`)**
*   **How it works**: Hosted as a Docker container on AWS/GCP/Kubernetes. The IDE connects over HTTP via Server-Sent Events (SSE).
*   **Why**: Used when the Vector DB is locked behind a strict corporate VPC that local laptops cannot access, or when running heavy local LLM-as-a-judge models that require cloud GPUs.
*   **Execution**: Teams deploy the RAGCheck Docker image, and developers add a URL (e.g., `https://ragcheck.internal.mycompany.com/mcp`) to their Cursor config.

**3. CI/CD Runner (Headless)**
*   **How it works**: Spun up ephemerally inside GitHub Actions or GitLab CI. An autonomous agent (like Antigravity) connects to it locally within the CI runner to evaluate and push commits.

```mermaid
graph TD
    IDE[AI IDE / Agent - Cursor, Windsurf, Claude] <-->|MCP (stdio) - Local Mode| MCPServer[Local RAGCheck MCP]
    IDE <-->|MCP (SSE) - Remote Mode| CloudMCP[Cloud RAGCheck MCP]
    
    MCPServer --> EvalEngine[Evaluation Engine]
    MCPServer --> DB[(Local SQLite .ragcheck/)]
    
    CloudMCP --> CloudEval[Distributed Eval Engine]
    CloudMCP --> CloudDB[(Enterprise PostgreSQL)]
```

### Technical Choices
*   **Core**: Python 3.11+.
*   **Protocol**: MCP (Model Context Protocol).
*   **Storage**: DuckDB/SQLite stored in `.ragcheck/` within the user's local workspace for fast analytical queries.
*   **Data Validation**: Pydantic v2 for strict JSON schemas returned to the AI agent.
*   **Evaluation Engine (BYOK)**: RAGCheck operates on a **Bring-Your-Own-Key (BYOK)** model. The MCP server does *not* provide LLM API access. Developers pass their own `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or custom endpoint URLs as environment variables to the MCP server configuration in their IDE. Under the hood, RAGCheck uses LiteLLM to universally route evaluation prompts to whichever provider the user configures.

---

## SECTION 15: MCP Tool Schemas

RAGCheck exposes exactly defined tools to the agent:

*   `ragcheck_analyze_workspace(docs_dir: str) -> dict`
*   `ragcheck_generate_tests(num_questions: int, difficulty: str) -> str` (Returns path to JSON dataset).
*   `ragcheck_evaluate_pipeline(test_dataset_path: str, rag_entrypoint_cmd: str) -> dict`
    *   *Returns*: `{"health_score": int, "failing_metrics": list, "failing_queries": list}`
*   `ragcheck_diagnose_issue(failing_queries: list) -> dict`
    *   *Returns*: `{"root_cause": str, "code_change_recommendation": str}`

---

## SECTION 16: Developer Experience (Walkthrough)

At no point does the developer leave their IDE.
1.  **Setup**: Developer installs the RAGCheck MCP server in Cursor (`cursor mcp add ragcheck`).
2.  **Interaction**: Developer types in Cursor Chat: *"Run RAGCheck and fix any issues."*
3.  **Observation**: The developer watches as Cursor generates tests, runs the RAG pipeline, diagnoses a low Context Recall, rewrites the `text_splitter.py` file, re-runs the tests, and reports a passing score.
4.  **Result**: The developer gets a hardened, production-ready RAG application without writing a single PyTest or reading an evaluation dashboard.

---

## SECTION 17: Distribution & Discovery Strategy

To ensure RAGCheck becomes the industry standard, developers must easily discover and install the MCP server.

### 1. Discovery Channels
*   **Official MCP Directories**: Getting RAGCheck listed in the official [Anthropic MCP Servers Directory](https://github.com/modelcontextprotocol/servers) and popular "Awesome MCP" lists.
*   **IDE Native Marketplaces**: Partnering with Cursor and Windsurf to feature RAGCheck in their internal "Tool/MCP Settings" menus as a recommended, one-click install.
*   **The "Trojan Horse" Integration**: Sponsoring or contributing official tutorials to the LangChain, LlamaIndex, and Haystack documentation (e.g., a page titled *"How to evaluate your LlamaIndex pipeline with the RAGCheck Agent"*).

### 2. Zero-Friction Installation
*   **Package Managers (`uv` and `npx`)**: Developers shouldn't have to clone a repo. They should just type:
    *   `uvx ragcheck-mcp@latest` (Python)
    *   `npx @ragcheck/mcp-server` (Node/TypeScript wrapper)
*   **Docker Container**: For enterprise deployment (`docker run -p 8080:8080 ragcheck/mcp-server`).

### 3. Open-Source Mechanics
*   **Licensing**: Apache 2.0.
*   **Repository Structure**: `ragcheck-mcp-server`, `ragcheck-core`.
*   **Plugin Ecosystem**: Community-driven metric plugins.
*   **Documentation**: Heavily focused on "How to use RAGCheck with Cursor", "How to use RAGCheck with Claude Code", and "How to use RAGCheck with Antigravity".

---

## SECTION 18: Future Roadmap

*   **Next 1-2 Years**: Agent-to-Agent Benchmarking. Using RAGCheck to evaluate complex multi-agent coding workflows (e.g., Devin vs. SWE-Agent).
*   **Autonomous Red Teaming**: The RAGCheck MCP server automatically runs jailbreak attempts against the user's local RAG code while they are developing it in the background.
*   **Self-Healing Production RAG**: Complete closed-loop systems where a production monitor detects a hallucination, pings an autonomous agent, the agent uses RAGCheck to write a fix locally, verifies it, and deploys it without human intervention.

---

## SECTION 19: Risks

*   **Technical Risk**: LLM-as-a-judge models are slow and expensive, frustrating the developer waiting in the IDE. *Mitigation*: Fallback to local small NLI models (DeBERTa) and aggressive caching of evaluation results in the local `.ragcheck/` SQLite DB.
*   **Agent Reliability**: The host agent (Cursor/Claude) might misunderstand the RAGCheck JSON output and write bad code. *Mitigation*: Extremely strict Pydantic schemas and highly prescriptive textual recommendations in the tool outputs.
*   **Business Risk**: AI IDEs build their own native evaluation tools. *Mitigation*: Position RAGCheck as the open standard MCP server that works across *all* IDEs and agents.

---

## SECTION 20: Phased Implementation Roadmap

### Phase 0: Research & Prototyping (Weeks 1-3)
*   **Deliverables**: Finalize Metric definitions, MCP Tool JSON schemas, and local database schema (DuckDB).
*   **Team**: 1 Principal Architect, 1 ML Researcher.

### Phase 1: Core Evaluation Engine & MCP Server (Weeks 4-8)
*   **Deliverables**: Basic Pydantic models for structured agent outputs, execution engine, Groundedness/Recall metrics, and the initial MCP Server exposing `ragcheck_evaluate_pipeline`.
*   **Acceptance Criteria**: Cursor/Claude can connect to the local MCP server, execute an evaluation against a dummy RAG script, and read the JSON response.

### Phase 2: Synthetic Question Generation (Weeks 9-12)
*   **Deliverables**: QCA generation pipeline via `ragcheck_generate_tests` MCP tool.
*   **Acceptance Criteria**: The AI Agent can invoke the tool to read a local `docs/` folder and generate 100 high-quality QCA pairs automatically.

### Phase 3: Retriever Diagnostics & Remediation Engine (Weeks 13-18)
*   **Deliverables**: The `ragcheck_diagnose_issue` tool. Building the logic that simulates different chunk sizes and retrieval strategies in the background.
*   **Acceptance Criteria**: The tool successfully outputs a JSON payload identifying "chunk_size_too_small" and suggests a specific token overlap change to the agent.

### Phase 4: CI/CD "Agentic PR Reviewer" (Weeks 19-22)
*   **Deliverables**: GitHub Actions runner that spins up an autonomous agent equipped with the RAGCheck MCP server to evaluate PRs and autonomously commit chunking/prompt fixes.

### Phase 5: IDE Visual Extensions (Weeks 23-28)
*   **Deliverables**: Native VS Code / Cursor extensions that consume the local MCP server to provide inline syntax-highlighting-style warnings for prompts and chunking logic that are at high risk of hallucination.

### Phase 6: Production-to-IDE Feedback Loop (Weeks 29-32)
*   **Deliverables**: Telemetry ingestion endpoint.
*   **Acceptance Criteria**: When a developer opens a RAG codebase in their IDE, the RAGCheck MCP server pulls the last 24 hours of production telemetry and tells the local AI agent which lines of code are failing in the real world.

---

## SECTION 21: Beta Testing & Go-To-Market Strategy

Releasing a tool meant for AI Agents requires a different beta testing approach than a traditional SaaS product. The goal of the beta is to validate that the MCP server correctly interfaces with various IDE agents (Cursor, Claude) and successfully diagnoses real-world RAG issues.

### 1. The "White-Glove" Alpha (10-15 Users)
*   **Target Audience**: Senior AI Engineers actively building RAG systems in production who already use Cursor or Windsurf daily.
*   **Distribution**: 
    *   Do not publish to public registries yet.
    *   Distribute the MCP server via a private, invite-only GitHub repository.
    *   Provide a 1-line installation script: `uvx git+https://github.com/ragcheck/ragcheck-mcp.git@main`.
*   **Onboarding**: The core team does a 30-minute Zoom call with the user to help them configure the MCP server in their IDE and run their first `ragcheck_analyze_workspace` scan.
*   **Feedback Loop**: Set up a private Slack/Discord channel. The primary metric is: *"Did the AI Agent successfully rewrite your code to fix a hallucination based on RAGCheck's output?"*

### 2. The Public Beta (Waitlist Model)
*   **Distribution**: 
    *   Publish the Python package to PyPI (`pip install ragcheck-mcp`).
    *   However, gate access to the advanced diagnostic models behind a free API key system (`RAGCHECK_API_KEY`).
*   **User Flow**:
    1.  Developer visits `ragcheck.io` and joins the waitlist.
    2.  Once approved, they receive an email with their API key and the setup instructions:
        ```json
        // Cursor Settings > MCP Servers
        {
          "name": "ragcheck",
          "command": "uvx",
          "args": ["ragcheck-mcp"],
          "env": { "RAGCHECK_API_KEY": "beta-key-123" }
        }
        ```
    3.  Developer opens their IDE and types: *"Run a RAGCheck scan."*
*   **Telemetry**: The MCP server (with explicit opt-in during beta) sends anonymized telemetry back to the team: which tools the agent called, how long the agent took to parse the JSON, and whether the agent successfully completed the workflow. (Never sending user source code or PDF contents).

### 3. The "Trojan Horse" Enterprise Pilot
*   **Strategy**: Identify 2-3 mid-sized enterprises struggling with RAG hallucinations in their customer support bots.
*   **Deployment**: Deploy the **Remote Enterprise Server (SSE)** model. Host the RAGCheck MCP server on an EC2 instance within their VPC.
*   **Goal**: Prove that an entire team of 5-10 developers can share a single RAGCheck server from their local Cursor IDEs without exfiltrating data, validating the Enterprise architecture.

---
*Document Version: 2.1.0 | Generated by AI Architect | Status: Approved for Implementation (Agentic MCP Pivot)*

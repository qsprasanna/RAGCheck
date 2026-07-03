import asyncio
import json
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

from .models import EvaluationReport, MetricScore, FixRecommendation

server = Server("ragcheck-mcp")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="ragcheck_analyze_workspace",
            description="Analyzes the local workspace documents to build the evaluation baseline and Knowledge Graph.",
            inputSchema={
                "type": "object",
                "properties": {
                    "docs_dir": {
                        "type": "string",
                        "description": "Path to the directory containing documents (PDFs, MDs)."
                    }
                },
                "required": ["docs_dir"]
            }
        ),
        types.Tool(
            name="ragcheck_generate_tests",
            description="Automatically generates a golden evaluation dataset (QCA pairs) from the analyzed workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "num_questions": {
                        "type": "integer",
                        "description": "Number of questions to generate."
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard", "mixed"],
                        "description": "Difficulty level of the questions."
                    },
                    "model": {
                        "type": "string",
                        "description": "The litellm model string to use for generation (e.g., 'gpt-4o-mini', 'claude-3-haiku-20240307'). Defaults to 'gpt-4o-mini'."
                    }
                },
                "required": ["num_questions"]
            }
        ),
        types.Tool(
            name="ragcheck_evaluate_pipeline",
            description="Evaluates a local RAG pipeline against the generated tests and returns an actionable health report with code fix recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_dataset_path": {
                        "type": "string",
                        "description": "Path to the generated JSON test dataset."
                    },
                    "rag_entrypoint_cmd": {
                        "type": "string",
                        "description": "Terminal command to query the local RAG pipeline (e.g., 'python query.py')."
                    },
                    "model": {
                        "type": "string",
                        "description": "The litellm model string to use for rigorous evaluation scoring (e.g., 'anthropic/claude-3-5-sonnet-20240620', 'gpt-4o'). Defaults to 'anthropic/claude-3-5-sonnet-20240620'."
                    }
                },
                "required": ["test_dataset_path", "rag_entrypoint_cmd"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    # Initialize DB (assumes current working directory is the workspace)
    import os
    from .db import WorkspaceDB
    from .ingestion import ingest_workspace
    from .generation import generate_synthetic_tests
    
    workspace_dir = os.getcwd()
    db = WorkspaceDB(workspace_dir)

    if name == "ragcheck_analyze_workspace":
        docs_dir = arguments.get("docs_dir", "./docs")
        try:
            total_chunks = ingest_workspace(docs_dir, db)
            result = f"✅ Successfully analyzed workspace at `{docs_dir}`. Extracted {total_chunks} chunks and built baseline Knowledge Graph in {db.db_path}."
        except Exception as e:
            result = f"❌ Error analyzing workspace: {str(e)}"
        return [types.TextContent(type="text", text=result)]

    elif name == "ragcheck_generate_tests":
        num_questions = arguments.get("num_questions", 10)
        difficulty = arguments.get("difficulty", "mixed")
        model = arguments.get("model", "gpt-4o-mini")
        try:
            output_path = generate_synthetic_tests(db, num_questions, difficulty, model)
            result = f"✅ Successfully generated {num_questions} synthetic tests using {model}. Saved to '{output_path}'."
        except Exception as e:
            result = f"❌ Error generating tests: {str(e)}"
        return [types.TextContent(type="text", text=result)]

    elif name == "ragcheck_evaluate_pipeline":
        test_dataset_path = arguments.get("test_dataset_path")
        rag_entrypoint_cmd = arguments.get("rag_entrypoint_cmd")
        model = arguments.get("model", "anthropic/claude-3-5-sonnet-20240620")
        
        try:
            from .evaluation import run_evaluation
            report = run_evaluation(test_dataset_path, rag_entrypoint_cmd, model)
            return [types.TextContent(type="text", text=report.model_dump_json(indent=2))]
        except Exception as e:
            return [types.TextContent(type="text", text=f'{{"error": "Failed to evaluate pipeline: {str(e)}"}}')]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ragcheck-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notificationOptions=NotificationOptions(),
                    experimentalCapabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())

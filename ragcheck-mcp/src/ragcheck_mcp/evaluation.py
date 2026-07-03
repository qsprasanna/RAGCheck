import json
import subprocess
import litellm
from pathlib import Path
from .models import EvaluationReport, MetricScore, FixRecommendation

def run_evaluation(test_dataset_path: str, rag_entrypoint_cmd: str, model: str = "anthropic/claude-3-5-sonnet-20240620") -> EvaluationReport:
    """
    Evaluates the RAG pipeline by running the entrypoint command for each test question,
    and then uses an LLM to grade the pipeline's answers.
    """
    path = Path(test_dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Test dataset not found at {test_dataset_path}")
        
    with open(path, "r", encoding="utf-8") as f:
        tests = json.load(f)

    results = []
    
    # Evaluate a max of 3 tests for the prototype to avoid long wait times
    tests_to_run = tests[:3]
    
    for test in tests_to_run:
        question = test["question"]
        ground_truth_context = test["context"]
        
        # 1. Query the user's RAG pipeline
        # We append the question to the command. Example: python query.py "What is X?"
        full_cmd = f'{rag_entrypoint_cmd} "{question}"'
        try:
            # Run the command and capture the output
            process = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)
            rag_answer = process.stdout.strip()
            if not rag_answer:
                rag_answer = "Error: RAG pipeline returned empty response."
        except subprocess.TimeoutExpired:
            rag_answer = "Error: RAG pipeline timed out."
        except Exception as e:
            rag_answer = f"Error: Failed to execute RAG pipeline: {e}"

        # 2. Grade the Answer using LiteLLM (Groundedness & Accuracy)
        eval_prompt = f"""
        You are an expert AI evaluator grading a RAG pipeline.
        
        Question asked: {question}
        Ground Truth Context: {ground_truth_context}
        Pipeline's Answer: {rag_answer}
        
        Evaluate the Pipeline's Answer based on the Ground Truth Context.
        Return a JSON object with strictly these keys:
        - "groundedness_score": float between 0.0 and 1.0 (is the answer faithful to the context?)
        - "groundedness_reasoning": string explaining why
        - "context_recall_score": float between 0.0 and 1.0 (did the answer include the relevant facts?)
        - "context_recall_reasoning": string explaining why
        """

        try:
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": eval_prompt}],
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            eval_result = json.loads(content)
            results.append(eval_result)
        except Exception as e:
            print(f"Failed to evaluate using litellm: {e}")
            # Fallback mock if LLM fails (e.g. missing API keys during testing)
            results.append({
                "groundedness_score": 0.5,
                "groundedness_reasoning": "Fallback due to LLM error.",
                "context_recall_score": 0.5,
                "context_recall_reasoning": "Fallback due to LLM error."
            })

    # Aggregate scores
    avg_groundedness = sum(r.get("groundedness_score", 0) for r in results) / len(results) if results else 0
    avg_recall = sum(r.get("context_recall_score", 0) for r in results) / len(results) if results else 0
    
    health_score = (avg_groundedness + avg_recall) / 2 * 100

    metrics = [
        MetricScore(name="groundedness", score=avg_groundedness, reasoning="Aggregated groundedness score across tests."),
        MetricScore(name="context_recall", score=avg_recall, reasoning="Aggregated context recall score across tests.")
    ]
    
    failing_metrics = []
    if avg_groundedness < 0.8:
        failing_metrics.append("groundedness")
    if avg_recall < 0.8:
        failing_metrics.append("context_recall")

    recommendations = []
    if "context_recall" in failing_metrics:
        recommendations.append(
            FixRecommendation(
                target_file="retriever.py", # Example file
                issue_description=f"Context recall is critically low ({avg_recall:.2f}). The retriever is failing to pull the correct chunks for the LLM to answer the questions.",
                recommended_action="increase_chunk_size",
                suggested_code_change="Review the chunking strategy. Consider increasing chunk_size or utilizing a hybrid search (BM25 + Vector) approach."
            )
        )
    if "groundedness" in failing_metrics:
        recommendations.append(
            FixRecommendation(
                target_file="prompt.py", # Example file
                issue_description=f"Groundedness is low ({avg_groundedness:.2f}). The generation model is hallucinating information not present in the retrieved context.",
                recommended_action="update_system_prompt",
                suggested_code_change="Add strict instructions to the system prompt: 'If the answer is not contained in the context, say I don't know. Do not make up facts.'"
            )
        )

    return EvaluationReport(
        health_score=health_score,
        metrics=metrics,
        failing_metrics=failing_metrics,
        recommendations=recommendations
    )

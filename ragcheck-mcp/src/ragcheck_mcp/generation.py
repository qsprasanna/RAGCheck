import random
import json
import litellm
from .db import WorkspaceDB

def generate_synthetic_tests(db: WorkspaceDB, num_questions: int, difficulty: str, model: str = "gpt-4o-mini") -> str:
    """Generates synthetic tests by pulling chunks and simulating QCA pairs."""
    chunks = db.get_all_chunks()
    if not chunks:
        raise ValueError("No chunks found in database. Please analyze workspace first.")
        
    generated_count = 0
    test_suite = []
    
    while generated_count < num_questions:
        # Pick a random chunk
        context = random.choice(chunks)
        
        # Call the LLM to generate a question and answer based on this context
        prompt = f"""
        You are an expert AI evaluator.
        Based on the following text chunk, generate a {difficulty} difficulty question and its correct answer.
        
        Text Chunk:
        {context}
        
        Return a JSON object with exactly two keys: "question" and "answer".
        """
        
        try:
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            content = response.choices[0].message.content
            qa_pair = json.loads(content)
            question = qa_pair.get("question", f"Generated question for chunk {generated_count}")
            answer = qa_pair.get("answer", f"Generated answer for chunk {generated_count}")
        except Exception as e:
            print(f"LLM generation failed: {e}")
            question = f"What information is provided in chunk {generated_count + 1}?"
            answer = f"The text chunk discusses the following: {context[:200]}"
        
        db.save_test(question, context, answer, difficulty)
        test_suite.append({
            "question": question,
            "context": context,
            "answer": answer,
            "difficulty": difficulty
        })
        generated_count += 1
        
    output_path = db.ragcheck_dir / "tests.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(test_suite, f, indent=2)
        
    return str(output_path)

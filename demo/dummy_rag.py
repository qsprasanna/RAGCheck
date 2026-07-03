import argparse

def query_pipeline(question: str) -> str:
    """
    A deliberately flawed mock RAG pipeline designed to fail RAGCheck evaluations.
    """
    question_lower = question.lower()
    
    if "work from home" in question_lower or "remote" in question_lower:
        # Deliberate Context Recall Failure: 
        # The retriever only pulls the first sentence of the policy and misses the 
        # exception clause for the Engineering team.
        return "Employees are allowed to work from home up to 2 days a week. The remaining 3 days must be spent in the office."
        
    elif "equipment" in question_lower or "stipend" in question_lower:
        # Deliberate Hallucination:
        # The true stipend is $1000, but the generation LLM hallucinated $2500.
        return "All new hires receive a $2500 equipment stipend for their home office setup. You have 90 days to expense it."
        
    elif "vacation" in question_lower or "pto" in question_lower:
        # Actually correct response
        return "The standard vacation policy is 15 days of PTO per year, and unused days do not roll over."
        
    else:
        return "I'm sorry, I don't have information about that in my knowledge base."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dummy RAG Pipeline")
    parser.add_argument("query", nargs="?", default="What is the work from home policy?", help="The user question")
    args = parser.parse_args()
    print(query_pipeline(args.query))

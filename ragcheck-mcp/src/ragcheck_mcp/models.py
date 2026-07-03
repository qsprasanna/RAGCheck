from pydantic import BaseModel, Field
from typing import List, Optional

class MetricScore(BaseModel):
    name: str = Field(description="Name of the metric (e.g., groundedness, context_recall)")
    score: float = Field(description="Score from 0.0 to 1.0")
    reasoning: str = Field(description="Explanation of why this score was given")

class FixRecommendation(BaseModel):
    target_file: str = Field(description="File to be modified")
    issue_description: str = Field(description="Description of what is failing")
    recommended_action: str = Field(description="What the agent should do to fix it (e.g., 'increase_chunk_size')")
    suggested_code_change: Optional[str] = Field(description="Specific code diff or parameter change")

class EvaluationReport(BaseModel):
    health_score: float = Field(description="Overall health score (0-100)")
    metrics: List[MetricScore]
    failing_metrics: List[str]
    recommendations: List[FixRecommendation]

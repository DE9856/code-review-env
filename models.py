from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ActionType(str, Enum):
    """Types of actions the agent can take"""
    SUBMIT_REVIEW = "submit_review"
    SKIP_TASK = "skip_task"

class CodeReviewAction(BaseModel):
    """Action space for code review agent"""
    action_type: ActionType = Field(..., description="Type of action to perform")
    content: str = Field(..., description="Review content or comment")
    line_numbers: Optional[List[int]] = Field(None, description="Specific line numbers being reviewed")

class CodeReviewObservation(BaseModel):
    """Observation space - what the agent sees"""
    diff: str = Field(..., description="Code diff to review")
    file_name: str = Field(..., description="Name of file being reviewed")
    language: str = Field(..., description="Programming language")
    step_count: int = Field(..., description="Current step number")
    max_steps: int = Field(..., description="Maximum steps allowed")
    task_id: str = Field(..., description="Current task ID")  # Changed from int to str
    difficulty: str = Field(..., description="Task difficulty: easy/medium/hard")

class CodeReviewState(BaseModel):
    """Complete environment state"""
    current_task_id: str  # Changed from int to str
    step_count: int
    done: bool
    accumulated_reward: float
    review_submitted: bool
    current_observation: Optional[CodeReviewObservation] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RewardInfo(BaseModel):
    """Reward information for step"""
    score: float = Field(..., ge=0.0, le=1.0)
    breakdown: Dict[str, float]
    feedback: str
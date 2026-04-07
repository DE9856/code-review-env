import json
import random
from pathlib import Path
from typing import Optional, Tuple, Dict
from models import (
    CodeReviewAction,
    CodeReviewObservation,
    CodeReviewState,
    RewardInfo
)


class CodeReviewEnvironment:
    """OpenEnv-compliant code review environment"""
    
    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.tasks = self._load_tasks()
        self.current_task = None
        self.step_count = 0
        self.done = False
        self.accumulated_reward = 0.0
        self.review_submitted = False
    
    def _load_tasks(self) -> dict:
        """Load tasks from JSON files"""
        tasks_dir = Path(__file__).parent / "tasks"
        tasks = {
            "easy": json.load(open(tasks_dir / "easy.json", encoding='utf-8')),
            "medium": json.load(open(tasks_dir / "medium.json", encoding='utf-8')),
            "hard": json.load(open(tasks_dir / "hard.json", encoding='utf-8'))
        }
        return tasks
    
    def reset(self, task_id: Optional[str] = None) -> CodeReviewObservation:
        """Reset environment and return initial observation"""
        self.step_count = 0
        self.done = False
        self.accumulated_reward = 0.0
        self.review_submitted = False
        self.current_task = None
        
        if task_id:
            # Find task by string ID
            for difficulty in ["easy", "medium", "hard"]:
                for task in self.tasks[difficulty]:
                    if task["id"] == task_id:
                        self.current_task = task
                        self.current_task["difficulty"] = difficulty
                        break
                if self.current_task:
                    break
            if self.current_task is None:
                raise ValueError(f"Unknown task_id: {task_id}")
        else:
            # Pick random task (weighted toward harder for testing)
            difficulty = random.choices(
                ["easy", "medium", "hard"],
                weights=[0.3, 0.3, 0.4]
            )[0]
            self.current_task = random.choice(self.tasks[difficulty])
            self.current_task["difficulty"] = difficulty
        
        return self._get_observation()
    
    def _get_observation(self) -> CodeReviewObservation:
        """Create observation from current state"""
        return CodeReviewObservation(
            diff=self.current_task["diff"],
            file_name=self.current_task.get("file_name", "unknown.py"),
            language=self.current_task.get("language", "python"),
            step_count=self.step_count,
            max_steps=self.max_steps,
            task_id=self.current_task["id"] if isinstance(self.current_task["id"], str) else str(self.current_task["id"]),
            difficulty=self.current_task["difficulty"]
        )
    
    def step(self, action: CodeReviewAction) -> Tuple[CodeReviewObservation, float, bool, dict]:
        """Execute action and return next state"""
        
        if self.done:
            return self._get_observation(), 0.0, True, {"error": "Episode already finished"}
        
        if action.action_type == "skip_task":
            self.done = True
            reward = -0.5
            self.accumulated_reward += reward
            return self._get_observation(), reward, True, {"skipped": True}
        
        # Grade based on difficulty
        difficulty = self.current_task["difficulty"]
        if difficulty == "easy":
            from graders.easy import grade_easy
            reward = grade_easy(action.content)
        elif difficulty == "medium":
            from graders.medium import grade_medium
            reward = grade_medium(action.content)
        else:
            from graders.hard import grade_hard
            reward = grade_hard(action.content)
        
        self.accumulated_reward += reward
        self.review_submitted = True
        self.step_count += 1
        self.done = True
        
        info = {
            "feedback": f"Score: {reward:.2f}",
            "step": self.step_count,
            "max_steps": self.max_steps,
            "task_id": self.current_task["id"],
            "difficulty": difficulty
        }
        
        return self._get_observation(), reward, self.done, info
    
    def state(self) -> CodeReviewState:
        """Return current environment state"""
        return CodeReviewState(
            current_task_id=str(self.current_task["id"]) if self.current_task else "-1",  # Convert to string
            step_count=self.step_count,
            done=self.done,
            accumulated_reward=self.accumulated_reward,
            review_submitted=self.review_submitted,
            current_observation=self._get_observation() if self.current_task else None,
            metadata={
                "difficulty": self.current_task["difficulty"] if self.current_task else "unknown",
                "max_steps": self.max_steps,
                "source": self.current_task.get("source", "unknown") if self.current_task else "unknown"
            }
        )
    
    def get_task_list(self) -> list:
        """Get all available tasks"""
        tasks = []
        for difficulty in ["easy", "medium", "hard"]:
            for task in self.tasks[difficulty]:
                tasks.append({
                    "id": task["id"],
                    "difficulty": difficulty,
                    "description": task.get("description", ""),
                    "file_name": task.get("file_name", "unknown"),
                    "source": task.get("source", "synthetic")
                })
        return tasks
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import sys
from pathlib import Path
import os
sys.path.append(os.getcwd())

from environment import CodeReviewEnvironment
from models import CodeReviewAction, CodeReviewObservation, CodeReviewState

app = FastAPI(title="Code Review Environment", description="OpenEnv for code review tasks")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance
env = CodeReviewEnvironment(max_steps=10)

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Code Review Environment", "version": "1.0.0"}

@app.post("/reset")
async def reset(task_id: str = None) -> CodeReviewObservation:
    """Reset environment and return initial observation"""
    try:
        observation = env.reset(task_id=task_id)
        return observation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step(action: CodeReviewAction) -> Dict[str, Any]:
    """Take action in environment"""
    try:
        observation, reward, done, info = env.step(action)
        return {
            "observation": observation.dict(),
            "reward": reward,
            "done": done,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def get_state() -> CodeReviewState:
    """Get current environment state"""
    try:
        state = env.state()
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def get_tasks() -> list:
    """Get list of available tasks"""
    try:
        tasks = env.get_task_list()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
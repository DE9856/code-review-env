from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import sys
import os

# Fix imports for Docker / HF
sys.path.append(os.getcwd())

from environment import CodeReviewEnvironment
from models import CodeReviewAction, CodeReviewObservation, CodeReviewState, ActionType
from inference import run_inference   # 🔥 NEW

app = FastAPI(
    title="Code Review Environment",
    description="OpenEnv for code review tasks"
)

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

# -------------------------
# Health Check
# -------------------------
from fastapi.responses import FileResponse

@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")

# -------------------------
# Environment APIs
# -------------------------

@app.post("/reset")
async def reset(task_id: str = None) -> CodeReviewObservation:
    try:
        return env.reset(task_id=task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step")
async def step(action: CodeReviewAction) -> Dict[str, Any]:
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
    try:
        return env.state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks")
async def get_tasks() -> list:
    try:
        return env.get_task_list()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# 🔥 INFERENCE API (NEW)
# -------------------------

@app.post("/infer")
async def infer(data: Dict[str, Any]):
    """
    Run code review inference using LLM
    """
    try:
        result = run_inference(
            diff=data.get("diff"),
            file_name=data.get("file_name"),
            language=data.get("language"),
            description=data.get("description"),
            difficulty=data.get("difficulty", "easy")
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auto_infer")
async def auto_infer(task_id: str):
    """
    Automatically run inference on a task from your dataset
    """
    try:
        # Reset environment with task
        obs = env.reset(task_id=task_id)

        # Get task metadata
        tasks = env.get_task_list()
        task_info = next((t for t in tasks if t["id"] == task_id), None)

        if not task_info:
            raise HTTPException(status_code=404, detail="Task not found")

        # Run inference
        result = run_inference(
            diff=obs.diff,
            file_name=obs.file_name,
            language=obs.language,
            description=task_info.get("description", ""),
            difficulty=task_info.get("difficulty", "easy")
        )

        return {
            "task_id": task_id,
            "input": {
                "diff": obs.diff,
                "file_name": obs.file_name,
                "language": obs.language
            },
            "output": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/run_all_tasks")
async def run_all_tasks():
    """
    Run inference on ALL tasks (like old inference.py)
    """
    try:
        tasks = env.get_task_list()

        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found")

        all_results = []
        all_rewards = []

        for task_info in tasks:
            task_id = task_info["id"]

            # Reset env
            obs = env.reset(task_id=task_id)

            # Run inference
            result = run_inference(
                diff=obs.diff,
                file_name=obs.file_name,
                language=obs.language,
                description=task_info.get("description", ""),
                difficulty=task_info.get("difficulty", "easy")
            )

            # Create action
            action = CodeReviewAction(
                action_type=ActionType.SUBMIT_REVIEW,
                content=result["formatted_submission"]
            )

            # Step environment (evaluation)
            obs, reward, done, info = env.step(action)

            all_rewards.append(reward)

            all_results.append({
                "task_id": task_id,
                "difficulty": task_info.get("difficulty"),
                "reward": reward,
                "done": done,
                "review": result["review"],
                "complexity": result["complexity"]
            })

        avg_score = sum(all_rewards) / len(all_rewards) if all_rewards else 0.0

        return {
            "total_tasks": len(all_results),
            "average_score": avg_score,
            "results": all_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
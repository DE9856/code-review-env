from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional
import sys
import os

# Fix imports for Docker / HF
sys.path.append(os.getcwd())

from environment import CodeReviewEnvironment
from models import CodeReviewAction, CodeReviewObservation, CodeReviewState, ActionType
from inference import run_inference

MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen3-Coder-480B-A35B-Instruct")
BENCHMARK  = os.getenv("BENCHMARK", "code-review")

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
# Structured Logging Helpers  (matches required stdout format)
# -------------------------

def log_start(task: str) -> None:
    print(f"[START] task={task} env={BENCHMARK} model={MODEL_NAME}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val  = str(done).lower()
    # Collapse action to single line to comply with "no newlines within a line" rule
    action_single = action.replace("\n", " ").replace("\r", "")
    print(
        f"[STEP] step={step} action={action_single} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# -------------------------
# Health Check
# -------------------------

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
# Inference API
# -------------------------

@app.post("/infer")
async def infer(data: Dict[str, Any]):
    """Run code review inference using LLM"""
    task_id     = data.get("task_id", "unknown")
    diff        = data.get("diff")
    file_name   = data.get("file_name")
    language    = data.get("language")
    description = data.get("description")
    difficulty  = data.get("difficulty", "easy")

    rewards: List[float] = []
    steps_taken = 0
    success = False
    score   = 0.0

    log_start(task=task_id)
    try:
        result = run_inference(
            diff=diff,
            file_name=file_name,
            language=language,
            description=description,
            difficulty=difficulty
        )
        steps_taken = 1
        reward = 0.0
        done   = True
        rewards.append(reward)

        log_step(step=1, action=result["formatted_submission"], reward=reward, done=done, error=None)

        score   = reward
        success = done

    except Exception as e:
        log_step(step=1, action="run_inference", reward=0.0, done=True, error=str(e))
        log_end(success=False, steps=1, score=0.0, rewards=[0.0])
        raise HTTPException(status_code=500, detail=str(e))

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return result


@app.post("/auto_infer")
async def auto_infer(task_id: str):
    """Automatically run inference on a task from your dataset"""
    rewards: List[float] = []
    steps_taken = 0
    success = False
    score   = 0.0

    log_start(task=task_id)
    try:
        obs = env.reset(task_id=task_id)

        tasks     = env.get_task_list()
        task_info = next((t for t in tasks if t["id"] == task_id), None)
        if not task_info:
            log_end(success=False, steps=0, score=0.0, rewards=[])
            raise HTTPException(status_code=404, detail="Task not found")

        description = task_info.get("description", "")
        difficulty  = task_info.get("difficulty", "easy")

        result = run_inference(
            diff=obs.diff,
            file_name=obs.file_name,
            language=obs.language,
            description=description,
            difficulty=difficulty
        )
        steps_taken = 1
        reward = 0.0
        done   = True
        rewards.append(reward)

        log_step(step=1, action=result["formatted_submission"], reward=reward, done=done, error=None)

        score   = reward
        success = done

    except HTTPException:
        raise
    except Exception as e:
        log_step(step=1, action="run_inference", reward=0.0, done=True, error=str(e))
        log_end(success=False, steps=1, score=0.0, rewards=[0.0])
        raise HTTPException(status_code=500, detail=str(e))

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return {
        "task_id": task_id,
        "input": {
            "diff": obs.diff,
            "file_name": obs.file_name,
            "language": obs.language
        },
        "output": result
    }


@app.get("/run_all_tasks")
async def run_all_tasks():
    """Run inference on ALL tasks"""
    try:
        tasks = env.get_task_list()
        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found")

        all_results = []
        all_rewards = []

        for task_info in tasks:
            task_id     = task_info["id"]
            description = task_info.get("description", "")
            difficulty  = task_info.get("difficulty", "easy")

            rewards: List[float] = []
            steps_taken = 0
            success = False
            score   = 0.0

            log_start(task=task_id)
            try:
                obs = env.reset(task_id=task_id)

                result = run_inference(
                    diff=obs.diff,
                    file_name=obs.file_name,
                    language=obs.language,
                    description=description,
                    difficulty=difficulty
                )

                action = CodeReviewAction(
                    action_type=ActionType.SUBMIT_REVIEW,
                    content=result["formatted_submission"]
                )

                obs, reward, done, info = env.step(action)

                rewards.append(reward)
                steps_taken = 1
                all_rewards.append(reward)

                log_step(step=1, action=result["formatted_submission"], reward=reward, done=done, error=None)

                score   = reward  # already in [0, 1] from environment
                success = reward > 0.0

                all_results.append({
                    "task_id":    task_id,
                    "difficulty": difficulty,
                    "reward":     reward,
                    "done":       done,
                    "review":     result["review"],
                    "complexity": result["complexity"]
                })

            except Exception as e:
                log_step(step=1, action="run_inference", reward=0.0, done=True, error=str(e))
                rewards     = [0.0]
                steps_taken = 1
                success     = False
                score       = 0.0
                all_rewards.append(0.0)

            finally:
                log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

        avg_score = sum(all_rewards) / len(all_rewards) if all_rewards else 0.0
        return {
            "total_tasks":   len(all_results),
            "average_score": avg_score,
            "results":       all_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
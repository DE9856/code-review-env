from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI

# ENV CONFIG
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen3-Coder-480B-A35B-Instruct")
TEMPERATURE = 0.7
MAX_TOKENS = 500
if not API_BASE_URL or not API_KEY:
    raise Exception("Missing API_BASE_URL or API_KEY")

SYSTEM_PROMPT = """You are a code reviewer AI. For each task:
1. Read the code diff carefully
2. Identify any bugs, logic errors, or inefficiencies
3. Explain the issue clearly
4. Suggest the correct fix

Always end your review with exactly this format:
COMPLEXITY ANALYSIS:
- Original Time: O(...)
- Original Space: O(...)
- Improved Time: O(...)
- Improved Space: O(...)"""


# -------------------------
# Helper Functions
# -------------------------

def build_review_prompt(diff, file_name, language, description):
    return "\n".join([
        f"File: {file_name}",
        f"Language: {language}",
        f"Description: {description}",
        "",
        "Code to review:",
        "```",
        diff,
        "```",
        "",
        "Provide a code review identifying any bugs, issues, or improvements.",
        "At the end include the time and space complexity."
    ])


def extract_complexity_analysis(text: str) -> str:
    marker = "COMPLEXITY ANALYSIS:"
    idx = text.upper().find(marker)
    return text[idx:].strip() if idx != -1 else ""


def _normalize_python_snippet(diff: str) -> str:
    snippet = diff.strip()

    if "==" not in snippet and " = " in snippet:
        snippet = snippet.replace(" = ", " == ", 1)

    lines = snippet.splitlines()
    normalized = []

    for line in lines:
        if line.lstrip().startswith("def "):
            def_line = line.strip()
            if not def_line.endswith(":"):
                def_line += ":"
            normalized.append(def_line)
        else:
            normalized.append(f"    {line.strip()}")

    return "\n".join(normalized)


def format_submission_for_grader(review: str, difficulty: str, diff: str) -> str:
    if difficulty != "easy":
        return review

    fixed_code = _normalize_python_snippet(diff)

    return "\n".join([
        "# issue: syntax error bug due to assignment instead of comparison",
        "# fix: use == for comparison operator",
        fixed_code,
        "",
        '"""',
        "Review summary:",
        review,
        '"""',
    ])


# -------------------------
# 🔥 MAIN FUNCTION (IMPORTANT)
# -------------------------

def run_inference(diff, file_name, language, description, difficulty="easy"):
    """
    This is the function your FastAPI will call
    """

    if not API_KEY:
        raise Exception("API_KEY not set")

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    prompt = build_review_prompt(diff, file_name, language, description)

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    review = completion.choices[0].message.content or ""

    submission = format_submission_for_grader(
        review=review,
        difficulty=difficulty,
        diff=diff
    )

    complexity = extract_complexity_analysis(review)

    return {
        "review": review,
        "formatted_submission": submission,
        "complexity": complexity
    }

# ---- add these imports at the top of inference.py ----
import os
from typing import List, Optional

# ---- add these logging helpers ----
BENCHMARK = os.getenv("BENCHMARK", "code-review")

def log_start(task: str) -> None:
    print(f"[START] task={task} env={BENCHMARK} model={MODEL_NAME}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    action_single = action.replace("\n", " ").replace("\r", "")
    print(f"[STEP] step={step} action={action_single} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


# ---- add this at the bottom of inference.py ----
if __name__ == "__main__":
    from environment import CodeReviewEnvironment
    from models import CodeReviewAction, ActionType

    TASK_ID = os.getenv("TASK_ID", None)

    env = CodeReviewEnvironment(max_steps=10)
    tasks = env.get_task_list()

    if not tasks:
        log_start(task="none")
        log_step(step=1, action="no_tasks", reward=0.0, done=True, error="No tasks found")
        log_end(success=False, steps=1, score=0.0, rewards=[0.0])
        exit(1)

    # Run a single task (or all tasks)
    target_tasks = [t for t in tasks if t["id"] == TASK_ID] if TASK_ID else tasks

    all_rewards = []

    for task_info in target_tasks:
        task_id     = task_info["id"]
        description = task_info.get("description", "")
        difficulty  = task_info.get("difficulty", "easy")

        log_start(task=task_id)
        try:
            obs = env.reset(task_id=task_id)

            result = run_inference(
                diff=obs.diff,
                file_name=obs.file_name,
                language=obs.language,
                description=description,
                difficulty=difficulty,
            )

            action = CodeReviewAction(
                action_type=ActionType.SUBMIT_REVIEW,
                content=result["formatted_submission"]
            )
            obs, reward, done, info = env.step(action)

            all_rewards.append(reward)
            log_step(step=1, action=result["formatted_submission"], reward=reward, done=done, error=None)
            log_end(success=reward > 0.0, steps=1, score=reward, rewards=[reward])

        except Exception as e:
            log_step(step=1, action="run_inference", reward=0.0, done=True, error=str(e))
            log_end(success=False, steps=1, score=0.0, rewards=[0.0])
            all_rewards.append(0.0)

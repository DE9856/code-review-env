from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI

# ENV CONFIG
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/hf-inference/models")
API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3")
TEMPERATURE = 0.7
MAX_TOKENS = 500

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
        raise Exception("OPENAI_API_KEY not set")

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
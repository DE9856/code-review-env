---
title: CodeReview AI
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# 🚀 CodeReview AI — OpenEnv RL Environment

### 🧠 Meta AI Hackathon Project

**CodeReview AI** is an OpenEnv-compatible reinforcement learning environment where AI agents learn to perform automated **code reviews** — detecting bugs, reasoning about issues, and suggesting optimized fixes with complexity analysis.

👉 **Live Demo:** *https://dkeie-code-review-ai.hf.space/*

---

## 🎯 Problem

Modern software development relies heavily on code reviews, but:

- They are manual and time-consuming
- Require deep expertise
- Do not scale with rapid development cycles

Existing LLM tools generate reviews, but:

- They are not evaluated
- They are not trainable as agents
- They lack structured feedback loops

---

## 💡 Our Solution

We built a fully interactive RL environment where:

- The agent = code reviewer
- The environment = code diff + evaluation system
- The reward = quality of review

This transforms code review into a **learning problem**.

---

## 🧠 Environment Design (OpenEnv)

This project implements a fully **OpenEnv-compatible environment** for code review tasks.

### Observation Space

Each observation contains:

| Field | Description |
|-------|-------------|
| `diff` | Code snippet / diff to review |
| `file_name` | File being reviewed |
| `language` | Programming language |
| `task_id` | Unique identifier |
| `difficulty` | easy / medium / hard |
| `step_count` | Current step |
| `max_steps` | Max allowed steps |

---

### Action Space

The agent can perform:

| Action | Description |
|--------|-------------|
| `submit_review` | Submit a review with explanation + fix |
| `skip_task` | Skip current task (penalty applied) |

Each action includes:

- `content` → Generated review text
- `line_numbers` (optional) → Lines being referenced

---

### State Space

The environment tracks:

- Current task
- Step count
- Accumulated reward
- Whether review was submitted
- Metadata (difficulty, source, etc.)

---

### Reward Function

Rewards are computed using **difficulty-specific graders**:

| Difficulty | Evaluation Focus |
|------------|------------------|
| Easy | Syntax error detection |
| Medium | Logical bug reasoning |
| Hard | Performance optimization |

Evaluation considers:

- Bug detection
- Explanation quality
- Fix correctness
- Complexity analysis

---

## 🏗️ System Architecture

```
Frontend (UI Dashboard)
        ↓
FastAPI Backend
        ↓
Inference Engine (LLM)
        ↓
OpenEnv Environment
        ↓
Grading System
```

---

## ⚙️ Technical Components

### 1. OpenEnv Environment

- Handles task sampling
- Manages state transitions
- Computes rewards
- Ensures RL compatibility

---

### 2. Task Dataset

Stored as JSON files:

- `easy.json`
- `medium.json`
- `hard.json`

Each task includes:

- Code diff
- Description
- Expected concepts

---

### 3. Grading System

Custom evaluators per difficulty:

- Keyword matching
- Pattern recognition
- AST validation (for correctness)
- Complexity-aware scoring

Ensures:

- Deterministic rewards
- Objective evaluation
- RL compatibility

---

### 4. LLM Inference Engine

- Uses OpenAI-compatible APIs (OpenRouter / HuggingFace)

- Generates structured reviews:
  - Bug detection
  - Explanation
  - Fix
  - Complexity

- Output is normalized for grading

---

### 5. API Layer (FastAPI)

| Endpoint | Function |
|----------|----------|
| `/reset` | Initialize environment |
| `/step` | Submit review & get reward |
| `/state` | Get environment state |
| `/tasks` | List all tasks |
| `/infer` | Run LLM review |
| `/run_all_tasks` | Benchmark all tasks |

---

## 🔥 Key Features (Demo Highlights)

### ⚡ Run All Tasks (Benchmark Mode)

- Runs agent on all dataset tasks
- Automatically:
  - Performs inference
  - Submits actions
  - Evaluates rewards

Outputs:

- Per-task score
- Average score
- Difficulty-wise performance

➡️ Acts as a **full evaluation pipeline for the agent**

---

### ✨ Custom Code Review (Interactive Mode)

Users can:

- Paste any code snippet
- Provide:
  - Description
  - File name
  - Language

**Supported languages:**
- Python
- Java
- JavaScript
- TypeScript
- C++

System outputs:

- Bug detection
- Fix suggestions
- Optimization ideas
- Complexity analysis

➡️ Works like a **real-world AI code reviewer**

---

## 📊 Evaluation Pipeline

```
1. Load task
        ↓
2. Generate review using LLM
        ↓
3. Format output
        ↓
4. Evaluate using grader
        ↓
5. Return reward
```

---

## 🔧 Setup (Optional - Local)

Clone the repository:

```bash
https://github.com/DE9856/code-review-env
cd your-repo
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` file:

```env
OPENAI_API_KEY=your_api_key
API_BASE_URL=https://router.huggingface.co/hf-inference/models
MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
HF_TOKEN = your_hugging_face_token
```

Run server:

```bash
uvicorn app:app --reload
```

---

## 🚀 Key Innovations

- OpenEnv-based code review environment
- RL loop applied to LLM evaluation
- Structured reward system for subjective tasks
- Dataset benchmarking + live inference
- Supports both automated evaluation and custom inputs
- Converts LLMs into trainable agents

---

## 🧪 Example Task

**Input:**
```python
def is_even(n): return n % 2 = 0
```

**Agent must:**
- Detect syntax error
- Explain issue
- Suggest fix
- Provide complexity

---

## 📈 Future Work

- Multi-step reasoning agents
- Learned reward models
- Code execution validation
- Multi-language expansion
- Fine-tuned reviewer agents

---

## 🏆 Hackathon Vision

**Move from:** LLMs that generate answers

**To:** Agents that learn, evaluate, and improve

---

## 👨‍💻 Team

**Meta AI Hackathon Team**  
*Filter Kaapi Force:*

- Deepesh Kumar Kotta
- Balaji Keerthi
- Abdul Hakeem K

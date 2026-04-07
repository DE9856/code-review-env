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

## 🧠 Core Idea

We combine:

- LLMs (reasoning + generation)
- OpenEnv (agent-environment interaction)
- Custom reward functions (evaluation)

➡️ Enabling **trainable code-review agents**

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

## ⚙️ Technical Breakdown

### 1. OpenEnv Environment

Implements a reinforcement learning loop:

**Observation:**
- Code diff
- File metadata
- Task difficulty

**Actions:**
- `submit_review`
- `skip_task`

**Tracks:**
- Step count
- Rewards
- Task state

**Reward based on:**
- Bug detection
- Reasoning quality
- Fix correctness

---

### 2. Task Design

Tasks are divided into 3 difficulty levels:

| Level | Type | Example |
|-------|------|---------|
| Easy | Syntax errors | `=` instead of `==` |
| Medium | Logical bugs | Wrong initialization |
| Hard | Algorithmic inefficiency | O(n²) → O(n) |

Each task is stored in JSON datasets and dynamically loaded.

---

### 3. Grading System

Each difficulty uses a custom evaluator:

- Keyword + pattern-based scoring
- AST validation (for code correctness)
- Complexity-aware scoring

Ensures:

- Deterministic rewards
- Objective evaluation
- RL compatibility

---

### 4. LLM Inference Engine

- Uses OpenAI-compatible APIs (OpenRouter / HuggingFace)

- Structured prompting:
  - Bug detection
  - Explanation
  - Fix suggestion
  - Complexity analysis

- Output is:
  - Parsed
  - Normalized
  - Converted into grader-compatible format

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

- Executes the agent across **all tasks in JSON datasets**
- Automatically:
  - Runs inference
  - Submits reviews
  - Evaluates rewards
- Outputs:
  - Score per task
  - Average score
  - Performance across difficulty levels

➡️ Acts as a **full evaluation pipeline for the agent**

---

### ✨ Custom Code Review (Interactive Mode)

Users can:

- Paste any code snippet
- Provide:
  - Description (what code should do)
  - File name
  - Language

**Supported languages:**
- Python
- Java
- JavaScript
- TypeScript
- C++

The system will:

- Analyze the code
- Detect bugs / inefficiencies
- Suggest fixes
- Provide complexity analysis

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

## 🚀 Key Innovations

- OpenEnv-based code review environment
- Full RL loop for LLM evaluation
- Structured reward system for subjective tasks
- Converts LLMs into trainable agents
- Built-in benchmarking + real-time UI
- Supports both **dataset evaluation** and **custom inputs**

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

Meta AI Hackathon Team
Filter Kaapi Force:
Deepesh Kumar Kotta
Balaji Keerthi
Abdul Hakeem K

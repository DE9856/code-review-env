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

- LLMs (for reasoning and generation)
- OpenEnv (for agent-environment interaction)
- Custom reward functions (for evaluation)

This enables **trainable code-review agents**.

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

**Easy** — Syntax errors
Example: "=" instead of "=="

**Medium** — Logical bugs
Example: wrong initialization or edge cases

**Hard** — Algorithmic inefficiency
Example: O(n²) → O(n) optimization

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

Endpoints:

- `/reset` → Initialize environment
- `/step` → Submit review & get reward
- `/state` → Get environment state
- `/tasks` → List all tasks
- `/infer` → Run LLM review
- `/run_all_tasks` → Benchmark all tasks

---

### 6. Frontend (Interactive UI)

- Run benchmark across all tasks

- View:
  - Scores
  - Complexity improvements
  - Task difficulty

- Custom mode:
  - Paste code
  - Get AI review instantly

---

## 📊 Evaluation Pipeline

1. Load task
2. Generate review using LLM
3. Format output
4. Evaluate using grader
5. Return reward

---

## 🚀 Key Innovations

- OpenEnv-based code review environment
- Full RL loop for LLM evaluation
- Structured reward system for subjective tasks
- Converts LLMs into trainable agents
- Supports automated benchmarking

---

## 🧪 Example Task

Input: def is_even(n): return n % 2 = 0


Agent must:

- Detect syntax error
- Explain issue
- Suggest fix
- Provide complexity

---

## 📈 Future Work

- Multi-step reasoning agents
- Learned reward models
- Code execution validation
- Multi-language support
- Fine-tuned reviewer models

---

## 🏆 Hackathon Vision

Move from:
LLMs that generate answers

To:
Agents that learn, evaluate, and improve

---

## 👨‍💻 Team
Meta AI Hackathon Team
Filter Kaapi Force:
  -> Deepesh Kumar Kotta
  -> Abdul Hakeem K
  -> Balaji Keerthi

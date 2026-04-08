import ast
import re

def contains_any(text, keywords):
    return any(k in text for k in keywords)

def grade_easy(output):
    output = output.lower()
    score = 0.0
    # Detection
    if contains_any(output, [
        "error", "syntax", "invalid", "wrong",
        "incorrect", "bug", "issue"
    ]):
        score += 0.3
    # Reasoning
    if contains_any(output, [
        "assignment", "comparison", "operator",
        "= instead of", "should be =="
    ]):
        score += 0.3
    # Fix
    if "==" in output or contains_any(output, ["equal", "comparison"]):
        try:
            tree = ast.parse(output)
            if any(isinstance(n, ast.FunctionDef) for n in tree.body):
                score += 0.4
        except:
            score += 0.2
    # Penalty
    if "looks fine" in output:
        score -= 0.5
    return max(0.01, min(score, 0.99))
def contains_any(text, keywords):
    return any(k in text for k in keywords)

def grade_medium(output):
    output = output.lower()
    score = 0.0
    # Detection
    if contains_any(output, [
        "logical", "wrong", "incorrect",
        "bug", "issue", "fails"
    ]):
        score += 0.3
    # Reasoning
    if contains_any(output, [
        "negative", "initialization",
        "edge case", "wrong initial"
    ]):
        score += 0.3
    # Fix
    if contains_any(output, [
        "lst[0]", "first element",
        "float('-inf')", "initialize"
    ]):
        score += 0.4
    # Penalty
    if "works fine" in output:
        score -= 0.5
    return max(0.01, min(score, 0.99))
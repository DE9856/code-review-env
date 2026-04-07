import re

def contains_any(text, keywords):
    return any(k in text for k in keywords)

def grade_hard(output):
    output = output.lower()
    score = 0.0
    
    # Detection - identify inefficiency
    if contains_any(output, [
        "inefficient", "slow", "nested loop",
        "quadratic", "brute force", "o(n^2)"
    ]):
        score += 0.3
    
    # Reasoning - explain complexity
    if re.search(r"o\(n\^?2\)", output) or contains_any(output, [
        "complexity", "n squared", "n^2", "quadratic time"
    ]):
        score += 0.3
    
    # Fix - suggest optimization
    if contains_any(output, [
        "set", "hash", "dictionary", "hashset",
        "o(n)", "linear", "use a set"
    ]):
        score += 0.4
    
    # Penalty - claiming wrong complexity
    if re.search(r"(already|is|runs in)\s*o\(n\)", output) and not re.search(r"o\(n\^?2\)|quadratic", output):
        score -= 0.3
    
    # Bonus - mentions both problems (list search and nested loops)
    if contains_any(output, ["list", "in operator", "contains"]) and contains_any(output, ["o(n^2)", "quadratic"]):
        score += 0.1
    
    return max(0.0, min(score, 1.0))
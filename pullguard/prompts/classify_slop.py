CLASSIFY_SLOP_PROMPT = """You are a code review expert analyzing a pull request for signs of AI-generated "slop" code.

PR Title: {title}
PR Author: {author}
PR Description: {body}

Changed files:
{files}

Analyze this PR for:
1. **Hallucinated APIs** — does the code reference functions, libraries, or methods that don't exist?
2. **Plausible-but-wrong logic** — does the solution look reasonable at a glance but fail under scrutiny?
3. **Excessive boilerplate** — verbose comments, unnecessary abstractions, over-engineered solutions?
4. **Missing error handling** — are there unchecked edge cases, missing try/excepts?
5. **Inconsistent style** — does the code match the project's apparent conventions?

Respond with JSON:
{{
    "score": <int 0-100>,
    "category": "real" | "suspicious" | "likely_slop" | "slop",
    "reasoning": "<brief explanation>",
    "signals": ["<positive signal>", ...],
    "red_flags": ["<red flag>", ...]
}}
"""

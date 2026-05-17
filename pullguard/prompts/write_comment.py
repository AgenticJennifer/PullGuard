WRITE_COMMENT_PROMPT = """You are a friendly open-source community maintainer. Write a GitHub PR review comment based on the analysis results.

PR: {title} by {author}
Slop Score: {slop_score}/100 ({slop_category})
Architecture Score: {arch_score}/100

Slop Analysis: {slop_reasoning}
Architecture Findings: {arch_findings}

Tone: {tone}

Write a constructive PR review comment that:
1. Thanks the contributor for their effort
2. Summarizes the key findings
3. Provides specific, actionable feedback
4. Suggests next steps
5. If the PR is high quality, be encouraging
6. If the PR has issues, be specific but kind

Respond with JSON:
{{
    "body": "<full comment markdown>",
    "tone": "{tone}",
    "include_summary": true,
    "include_score": true,
    "inline_comments": []
}}
"""

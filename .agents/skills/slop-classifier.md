# Slop Classifier

## Purpose
Generate a 0-100 quality score, confidence score, classification, and factor breakdown for each pull request.

## Guardrails
- Do not close PRs directly
- Do not insult contributors
- If confidence is low, return `needs_review`

# PullGuard

PullGuard is an AI-powered PR quality classification and auto-triage system for GitHub.

## Core loop

PR opened or updated -> PullGuard analyzes diff and repo context -> quality score + classification -> bounded action.

## MVP goals

- Score pull requests from 0-100
- Classify PRs as `slop`, `needs_review`, or `good`
- Apply labels and comments automatically
- Escalate low-confidence or destructive actions to a human

## Repository structure

```text
pullguard/
├── README.md
├── company.yaml
├── .agents/
│   ├── workflows/
│   │   └── pr-triage.yaml
│   ├── skills/
│   └── policies/
├── prompts/
│   ├── bootstrap/
│   └── heartbeat/
├── config/
├── docs/
├── server/
└── ui/
```

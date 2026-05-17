from __future__ import annotations
import json
import re
from pullguard.agents.base import BaseAgent
from pullguard.models import SlopAnalysis, SlopCategory, PullRequest
from pullguard.prompts.classify_slop import CLASSIFY_SLOP_PROMPT


class SlopClassifier(BaseAgent):
    async def run(self, pr: PullRequest, **kwargs) -> SlopAnalysis:
        files_text = self._format_files(pr)
        prompt = CLASSIFY_SLOP_PROMPT.format(
            title=pr.title,
            author=pr.author,
            body=pr.body or "(no description)",
            files=files_text,
        )
        response = await self.client.complete(prompt, temperature=0.3)
        result = self._parse_response(response)
        return SlopAnalysis(**result)

    def _format_files(self, pr: PullRequest) -> str:
        lines = []
        max_files = self.config.analysis.max_files_to_sample
        for f in pr.files[:max_files]:
            patch_excerpt = (f.patch or "")[:500]
            lines.append(f"## {f.filename} ({f.status}, +{f.additions}/-{f.deletions})")
            if patch_excerpt:
                lines.append(f"```diff\n{patch_excerpt}\n```")
        return "\n".join(lines)

    def _parse_response(self, text: str) -> dict:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {
            "score": 50,
            "category": "suspicious",
            "reasoning": "Failed to parse LLM response",
            "signals": [],
            "red_flags": [],
            "confidence": "low",
            "confidence_reason": "Could not parse LLM output",
        }

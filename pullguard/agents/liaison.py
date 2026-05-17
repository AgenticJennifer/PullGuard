from __future__ import annotations
import json
import re
from pullguard.agents.base import BaseAgent
from pullguard.models import CommentDraft, SlopAnalysis, ArchitectureAudit, PullRequest
from pullguard.prompts.write_comment import WRITE_COMMENT_PROMPT


class CommunityLiaison(BaseAgent):
    async def run(
        self,
        pr: PullRequest,
        slop: SlopAnalysis | None = None,
        architecture: ArchitectureAudit | None = None,
        **kwargs,
    ) -> CommentDraft:
        prompt = WRITE_COMMENT_PROMPT.format(
            title=pr.title,
            author=pr.author,
            slop_score=slop.score if slop else "N/A",
            slop_category=slop.category.value if slop else "N/A",
            arch_score=architecture.score if architecture else "N/A",
            slop_reasoning=slop.reasoning if slop else "(skipped)",
            arch_findings=self._format_findings(architecture),
            tone=self.config.community.tone,
        )
        model = self._build_model()
        response = await model.generate_content_async(prompt)
        result = self._parse_response(response.text)
        return CommentDraft(**result)

    def _format_findings(self, audit: ArchitectureAudit | None) -> str:
        if not audit or not audit.findings:
            return "(no findings)"
        return "; ".join(f"{f.severity}: {f.message}" for f in audit.findings[:5])

    def _parse_response(self, text: str) -> dict:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {
            "body": "Thank you for your contribution! The automated review is being processed.",
            "tone": "constructive",
            "include_summary": True,
            "include_score": True,
            "inline_comments": [],
        }

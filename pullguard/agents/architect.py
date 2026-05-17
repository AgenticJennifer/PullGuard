from __future__ import annotations
import json
import re
from pathlib import Path
from pullguard.agents.base import BaseAgent
from pullguard.models import ArchitectureAudit, ArchitectureFinding, PullRequest
from pullguard.prompts.audit_architecture import AUDIT_ARCHITECTURE_PROMPT


class ArchitectureAuditor(BaseAgent):
    async def run(self, pr: PullRequest, repo_path: str = ".", **kwargs) -> ArchitectureAudit:
        project_docs = self._load_project_docs(repo_path)
        files_text = self._format_files(pr)
        prompt = AUDIT_ARCHITECTURE_PROMPT.format(
            project_docs=project_docs,
            files=files_text,
        )
        response = await self.client.complete(prompt, temperature=0.3)
        result = self._parse_response(response)
        return ArchitectureAudit(**result)

    def _load_project_docs(self, repo_path: str) -> str:
        required = self.config.architect.required_dirs
        texts = []
        for pattern in required:
            for p in Path(repo_path).glob(pattern):
                if p.is_file() and p.suffix in (".md", ".txt", ".rst"):
                    texts.append(f"--- {p} ---\n{p.read_text()[:3000]}")
                elif p.is_dir():
                    for doc in list(p.glob("**/*.md"))[:self.config.architect.max_context_files]:
                        texts.append(f"--- {doc} ---\n{doc.read_text()[:3000]}")
        return "\n\n".join(texts) if texts else "(no project docs found)"

    def _format_files(self, pr: PullRequest) -> str:
        lines = []
        max_files = self.config.analysis.max_files_to_sample
        for f in pr.files[:max_files]:
            patch_excerpt = (f.patch or "")[:800]
            lines.append(f"## {f.filename} ({f.status})")
            if patch_excerpt:
                lines.append(f"```diff\n{patch_excerpt}\n```")
        return "\n".join(lines)

    def _parse_response(self, text: str) -> dict:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {
            "passed": False, "score": 50, "findings": [],
            "project_docs_used": [],
            "confidence": "low",
            "confidence_reason": "Could not parse LLM output",
        }

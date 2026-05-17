from __future__ import annotations
import asyncio
from pullguard.models import (
    PullRequest, AnalysisResult, SlopAnalysis, ArchitectureAudit,
    SlopCategory,
)
from pullguard.config import PullGuardConfig
from pullguard.agents.slop_classifier import SlopClassifier
from pullguard.agents.architect import ArchitectureAuditor
from pullguard.agents.liaison import CommunityLiaison


class Director:
    def __init__(self, config: PullGuardConfig, repo_path: str = "."):
        self.config = config
        self.repo_path = repo_path
        self.slop_classifier = SlopClassifier(config)
        self.architect = ArchitectureAuditor(config)
        self.liaison = CommunityLiaison(config)

    async def analyze(self, pr: PullRequest) -> AnalysisResult:
        slop: SlopAnalysis | None = None
        arch: ArchitectureAudit | None = None

        tasks = []

        if self.config.slop_classifier.enabled:
            tasks.append(self._run_slop(pr))
        if self.config.architect.enabled:
            tasks.append(self._run_arch(pr))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, SlopAnalysis):
                slop = r
            elif isinstance(r, ArchitectureAudit):
                arch = r
            elif isinstance(r, Exception):
                pass

        overall_score = self._compute_score(slop, arch)

        comment = None
        if self.config.community.enabled:
            comment = await self.liaison.run(pr=pr, slop=slop, architecture=arch)

        return AnalysisResult(
            pr_number=pr.number,
            slop=slop,
            architecture=arch,
            comment=comment,
            overall_score=overall_score,
        )

    async def _run_slop(self, pr: PullRequest) -> SlopAnalysis:
        return await self.slop_classifier.run(pr=pr)

    async def _run_arch(self, pr: PullRequest) -> ArchitectureAudit:
        return await self.architect.run(pr=pr, repo_path=self.repo_path)

    def _compute_score(
        self, slop: SlopAnalysis | None, arch: ArchitectureAudit | None
    ) -> int:
        scores = []
        if slop:
            scores.append(slop.score)
        if arch:
            scores.append(arch.score)
        if not scores:
            return 0
        return round(sum(scores) / len(scores))

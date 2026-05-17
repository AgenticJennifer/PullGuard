from __future__ import annotations
import asyncio
import logging
import time
from pullguard.models import (
    PullRequest, AnalysisResult, SlopAnalysis, ArchitectureAudit,
)
from pullguard.config import PullGuardConfig
from pullguard.agents.slop_classifier import SlopClassifier
from pullguard.agents.architect import ArchitectureAuditor
from pullguard.agents.liaison import CommunityLiaison
from pullguard.filters import DiffFilter
from pullguard.sampler import FileSampler

logger = logging.getLogger("pullguard.director")


class Director:
    def __init__(self, config: PullGuardConfig, repo_path: str = "."):
        self.config = config
        self.repo_path = repo_path
        self.slop_classifier = SlopClassifier(config)
        self.architect = ArchitectureAuditor(config)
        self.liaison = CommunityLiaison(config)
        self.diff_filter = DiffFilter(config)
        self.file_sampler = FileSampler(config)

    async def analyze(self, pr: PullRequest) -> AnalysisResult | None:
        start = time.monotonic()

        filter_result = self.diff_filter.evaluate(pr.files)
        if filter_result.should_skip:
            logger.info(
                "pr_skipped",
                extra={
                    "pr": pr.number,
                    "reason": filter_result.reason,
                    "lines_changed": filter_result.lines_changed,
                },
            )
            if self.config.analysis.skip_behaviour == "acknowledge":
                fallback_comment = self._build_skip_comment(pr, filter_result)
                return AnalysisResult(
                    pr_number=pr.number,
                    comment=fallback_comment,
                    flagged=False,
                )
            return None

        sampled = self.file_sampler.sample(pr.files)
        if sampled.sampled_count < sampled.total_files:
            logger.info(
                "file_sampling",
                extra={
                    "pr": pr.number,
                    "sampled": sampled.sampled_count,
                    "total": sampled.total_files,
                    "strategy": sampled.strategy_used,
                },
            )

        pr_sampled = PullRequest(
            number=pr.number,
            title=pr.title,
            body=pr.body,
            author=pr.author,
            base_branch=pr.base_branch,
            head_sha=pr.head_sha,
            files=sampled.files,
            url=pr.url,
        )

        slop: SlopAnalysis | None = None
        arch: ArchitectureAudit | None = None

        tasks = []

        if self.config.slop_classifier.enabled:
            tasks.append(self._run_timed("slop_classifier", self.slop_classifier.run, pr=pr_sampled))
        if self.config.architect.enabled:
            tasks.append(self._run_timed("architect", self.architect.run, pr=pr_sampled, repo_path=self.repo_path))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, SlopAnalysis):
                slop = r
            elif isinstance(r, ArchitectureAudit):
                arch = r
            elif isinstance(r, Exception):
                logger.warning("Agent raised", exc_info=r)

        flagged = self._is_flagged(slop, arch)
        comment = None
        if self.config.community.enabled:
            comment = await self.liaison.run(pr=pr_sampled, slop=slop, architecture=arch)

        elapsed = (time.monotonic() - start) * 1000
        logger.info(
            "analysis_complete",
            extra={
                "pr": pr.number,
                "slop_score": slop.score if slop else None,
                "arch_score": arch.score if arch else None,
                "flagged": flagged,
                "latency_ms": round(elapsed),
                "files_sampled": sampled.sampled_count,
                "files_total": sampled.total_files,
            },
        )

        return AnalysisResult(
            pr_number=pr.number,
            slop=slop,
            architecture=arch,
            comment=comment,
            flagged=flagged,
        )

    async def _run_timed(self, name: str, coro, **kwargs):
        start = time.monotonic()
        try:
            result = await coro(**kwargs)
            elapsed = (time.monotonic() - start) * 1000
            logger.info("agent_complete", extra={"agent": name, "latency_ms": round(elapsed)})
            return result
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            logger.warning("agent_failed", extra={"agent": name, "latency_ms": round(elapsed), "error": str(exc)})
            return exc

    def _is_flagged(self, slop: SlopAnalysis | None, arch: ArchitectureAudit | None) -> bool:
        if slop:
            slop_thresholds = self.config.slop_classifier.thresholds
            if slop.score < slop_thresholds.likely_slop:
                return True
        if arch:
            arch_thresholds = self.config.architect.thresholds
            if arch.score < arch_thresholds.major_violations:
                return True
        return False

    def _build_skip_comment(self, pr: PullRequest, filter_result) -> object:
        from pullguard.models import CommentDraft
        return CommentDraft(
            body=f"PullGuard skipped analysis for PR #{pr.number}: {filter_result.reason} ({filter_result.lines_changed} lines changed).",
            tone="neutral",
            include_summary=False,
            include_score=False,
        )

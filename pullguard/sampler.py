from __future__ import annotations
import fnmatch
from dataclasses import dataclass, field
from pullguard.config import PullGuardConfig
from pullguard.models import PRFile


@dataclass
class SampledResult:
    files: list[PRFile] = field(default_factory=list)
    total_files: int = 0
    sampled_count: int = 0
    strategy_used: str = ""


class FileSampler:
    def __init__(self, config: PullGuardConfig):
        self.config = config

    def sample(self, files: list[PRFile]) -> SampledResult:
        max_files = self.config.analysis.max_files_to_sample
        total = len(files)

        if total <= max_files:
            return SampledResult(
                files=files,
                total_files=total,
                sampled_count=total,
                strategy_used="none_needed",
            )

        strategy = self.config.analysis.sampling_strategy
        if strategy == "priority":
            return self._priority_sample(files, max_files)
        if strategy == "random":
            return self._random_sample(files, max_files)
        return self._truncate_sample(files, max_files)

    def _priority_sample(self, files: list[PRFile], max_files: int) -> SampledResult:
        patterns = self.config.architect.required_dirs
        scored: list[tuple[int, PRFile]] = []

        for f in files:
            priority = 0
            for pattern in patterns:
                if self._path_matches(f.filename, pattern):
                    priority += 1000
            priority += f.additions + f.deletions
            scored.append((priority, f))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [f for _, f in scored[:max_files]]

        return SampledResult(
            files=selected,
            total_files=len(files),
            sampled_count=len(selected),
            strategy_used="priority",
        )

    def _random_sample(self, files: list[PRFile], max_files: int) -> SampledResult:
        import random
        selected = random.sample(files, min(max_files, len(files)))
        return SampledResult(
            files=selected,
            total_files=len(files),
            sampled_count=len(selected),
            strategy_used="random",
        )

    def _truncate_sample(self, files: list[PRFile], max_files: int) -> SampledResult:
        return SampledResult(
            files=files[:max_files],
            total_files=len(files),
            sampled_count=max_files,
            strategy_used="truncate",
        )

    def _path_matches(self, path: str, pattern: str) -> bool:
        if pattern.endswith("/"):
            return path.startswith(pattern)
        return fnmatch.fnmatch(path, pattern)

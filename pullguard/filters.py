from __future__ import annotations
import fnmatch
from dataclasses import dataclass, field
from pullguard.config import PullGuardConfig
from pullguard.models import PRFile


@dataclass
class FilterResult:
    should_skip: bool
    reason: str = ""
    lines_changed: int = 0
    files_filtered: int = 0
    files_remaining: int = 0


class DiffFilter:
    def __init__(self, config: PullGuardConfig):
        self.config = config

    def evaluate(self, files: list[PRFile]) -> FilterResult:
        remaining: list[PRFile] = []
        total_lines = 0

        for f in files:
            if self._matches_skip_pattern(f.filename):
                continue
            remaining.append(f)
            total_lines += f.additions + f.deletions

        if not remaining:
            return FilterResult(
                should_skip=True,
                reason="only_skipped_files",
                lines_changed=total_lines,
                files_filtered=len(files),
                files_remaining=0,
            )

        min_lines = self.config.analysis.min_lines_changed
        if total_lines < min_lines:
            return FilterResult(
                should_skip=True,
                reason="below_min_diff",
                lines_changed=total_lines,
                files_filtered=len(files) - len(remaining),
                files_remaining=len(remaining),
            )

        return FilterResult(
            should_skip=False,
            lines_changed=total_lines,
            files_filtered=len(files) - len(remaining),
            files_remaining=len(remaining),
        )

    def _matches_skip_pattern(self, filename: str) -> bool:
        for pattern in self.config.analysis.skip_file_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

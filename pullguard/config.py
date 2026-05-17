from __future__ import annotations
from pathlib import Path
import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider: str = "gemini"
    model: str = "gemini-2.0-flash"
    temperature: float = 0.3
    api_key: str | None = None


class SlopThresholdsConfig(BaseModel):
    suspicious: int = 40
    likely_slop: int = 25


class ArchThresholdsConfig(BaseModel):
    minor_violations: int = 60
    major_violations: int = 40


class SlopClassifierConfig(BaseModel):
    enabled: bool = True
    thresholds: SlopThresholdsConfig = SlopThresholdsConfig()


class ArchitectConfig(BaseModel):
    enabled: bool = True
    thresholds: ArchThresholdsConfig = ArchThresholdsConfig()
    required_dirs: list[str] = ["docs/", "ARCHITECTURE.md"]
    max_context_files: int = 5


class CommunityConfig(BaseModel):
    enabled: bool = True
    tone: str = "constructive"
    mention_maintainer_on_score_below: int = 30
    allow_recheck_from: str = "author"


class AnalysisConfig(BaseModel):
    min_score: int = 50
    min_scores: dict[str, int] = Field(default_factory=lambda: {"slop": 25, "arch": 40})
    require_arch_audit: bool = True
    max_files_to_sample: int = 20
    sampling_strategy: str = "priority"
    min_lines_changed: int = 10
    skip_file_patterns: list[str] = Field(default_factory=lambda: ["*.md", "*.txt", "*.lock"])
    skip_behaviour: str = "silent"


class PullGuardConfig(BaseModel):
    version: int = 1
    analysis: AnalysisConfig = AnalysisConfig()
    llm: LLMConfig = LLMConfig()
    slop_classifier: SlopClassifierConfig = SlopClassifierConfig()
    architect: ArchitectConfig = ArchitectConfig()
    community: CommunityConfig = CommunityConfig()

    @classmethod
    def from_file(cls, path: str | Path) -> PullGuardConfig:
        path = Path(path)
        if not path.exists():
            return cls()
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def load_for_repo(cls, repo_path: str | Path = ".") -> PullGuardConfig:
        local_path = Path(repo_path) / ".github" / "pullguard.yml"
        return cls.from_file(local_path)

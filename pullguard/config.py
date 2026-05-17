from __future__ import annotations
from pathlib import Path
import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    model: str = "gemini-2.0-flash"
    temperature: float = 0.3
    api_key: str | None = None


class ThresholdsConfig(BaseModel):
    suspicious: int = 40
    likely_slop: int = 25


class SlopClassifierConfig(BaseModel):
    enabled: bool = True
    thresholds: ThresholdsConfig = ThresholdsConfig()


class ArchitectConfig(BaseModel):
    enabled: bool = True
    required_dirs: list[str] = ["docs/", "ARCHITECTURE.md"]
    max_context_files: int = 5


class CommunityConfig(BaseModel):
    enabled: bool = True
    tone: str = "constructive"
    mention_maintainer_on_score_below: int = 30


class AnalysisConfig(BaseModel):
    min_score: int = 50
    require_arch_audit: bool = True
    max_files_to_sample: int = 20


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

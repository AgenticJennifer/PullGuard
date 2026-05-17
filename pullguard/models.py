from __future__ import annotations
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class PRFile(BaseModel):
    filename: str
    status: str
    additions: int
    deletions: int
    patch: str | None = None
    raw_url: str | None = None


class PullRequest(BaseModel):
    number: int
    title: str
    body: str | None = None
    author: str
    base_branch: str
    head_sha: str
    files: list[PRFile] = []
    url: str
    created_at: datetime | None = None


class SlopCategory(str, Enum):
    REAL = "real"
    SUSPICIOUS = "suspicious"
    LIKELY_SLOP = "likely_slop"
    SLOP = "slop"


class SlopAnalysis(BaseModel):
    score: int = Field(ge=0, le=100)
    category: SlopCategory
    reasoning: str
    signals: list[str] = []
    red_flags: list[str] = []


class ArchitectureFinding(BaseModel):
    severity: str
    file: str | None = None
    message: str
    suggested_fix: str | None = None


class ArchitectureAudit(BaseModel):
    passed: bool
    score: int = Field(ge=0, le=100)
    findings: list[ArchitectureFinding] = []
    project_docs_used: list[str] = []


class InlineComment(BaseModel):
    path: str
    line: int
    body: str


class CommentDraft(BaseModel):
    body: str
    tone: str
    include_summary: bool = True
    include_score: bool = True
    inline_comments: list[InlineComment] = []


class AnalysisResult(BaseModel):
    pr_number: int
    slop: SlopAnalysis | None = None
    architecture: ArchitectureAudit | None = None
    comment: CommentDraft | None = None
    overall_score: int = Field(default=0, ge=0, le=100)
    error: str | None = None

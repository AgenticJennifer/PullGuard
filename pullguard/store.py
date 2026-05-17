from __future__ import annotations
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BaselineStats:
    slop_mean: float
    slop_stddev: float
    arch_mean: float
    arch_stddev: float
    sample_count: int


@dataclass
class OutlierResult:
    is_outlier: bool
    z_score: float


class ScoreStore:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.environ.get("PULLGUARD_DB_PATH", str(Path.home() / ".pullguard" / "scores.db"))
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo TEXT NOT NULL,
                    pr_number INTEGER NOT NULL,
                    slop_score INTEGER,
                    arch_score INTEGER,
                    analysed_at TEXT DEFAULT (datetime('now'))
                )
            """)

    def record(self, repo: str, pr_number: int, slop_score: int | None, arch_score: int | None) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO scores (repo, pr_number, slop_score, arch_score) VALUES (?, ?, ?, ?)",
                (repo, pr_number, slop_score, arch_score),
            )

    def baseline(self, repo: str, min_samples: int = 10) -> BaselineStats | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT AVG(slop_score), AVG(arch_score),
                       COUNT(*) as cnt
                FROM scores WHERE repo = ?
                """,
                (repo,),
            ).fetchone()

            if row is None or row[2] < min_samples:
                return None

            slop_mean = row[0] or 0
            arch_mean = row[1] or 0

            std = conn.execute(
                """
                SELECT AVG((slop_score - ?) * (slop_score - ?)),
                       AVG((arch_score - ?) * (arch_score - ?))
                FROM scores WHERE repo = ?
                """,
                (slop_mean, slop_mean, arch_mean, arch_mean, repo),
            ).fetchone()

            import math
            slop_std = math.sqrt(std[0]) if std and std[0] else 0
            arch_std = math.sqrt(std[1]) if std and std[1] else 0

            return BaselineStats(
                slop_mean=round(slop_mean, 1),
                slop_stddev=round(slop_std, 1),
                arch_mean=round(arch_mean, 1),
                arch_stddev=round(arch_std, 1),
                sample_count=row[2],
            )

    def is_outlier(self, repo: str, score: int, dimension: str, min_samples: int = 10) -> OutlierResult:
        stats = self.baseline(repo, min_samples=min_samples)
        if stats is None:
            return OutlierResult(is_outlier=False, z_score=0.0)

        mean = stats.slop_mean if dimension == "slop" else stats.arch_mean
        stddev = stats.slop_stddev if dimension == "slop" else stats.arch_stddev

        if stddev == 0:
            if score != mean:
                return OutlierResult(is_outlier=True, z_score=-10.0 if score < mean else 10.0)
            return OutlierResult(is_outlier=False, z_score=0.0)

        z_score = (score - mean) / stddev
        return OutlierResult(
            is_outlier=z_score < -1.5,
            z_score=round(z_score, 2),
        )

    def recent_analyses(self, repo: str | None = None, limit: int = 50) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            if repo:
                rows = conn.execute(
                    "SELECT repo, pr_number, slop_score, arch_score, analysed_at FROM scores WHERE repo = ? ORDER BY id DESC LIMIT ?",
                    (repo, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT repo, pr_number, slop_score, arch_score, analysed_at FROM scores ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()

            return [
                {
                    "repo": r[0],
                    "pr_number": r[1],
                    "slop_score": r[2],
                    "arch_score": r[3],
                    "analysed_at": r[4],
                }
                for r in rows
            ]

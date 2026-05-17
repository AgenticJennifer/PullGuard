import tempfile
from pathlib import Path
from pullguard.store import ScoreStore


def test_record_and_baseline():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        store = ScoreStore(db_path=db_path)
        for i in range(10):
            store.record("owner/repo", i, slop_score=50 + i, arch_score=60 + i)

        stats = store.baseline("owner/repo", min_samples=5)
        assert stats is not None
        assert stats.sample_count == 10
        assert 54 < stats.slop_mean < 55
        assert 64 < stats.arch_mean < 65
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_baseline_not_enough_samples():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        store = ScoreStore(db_path=db_path)
        store.record("owner/repo", 1, slop_score=50, arch_score=60)
        stats = store.baseline("owner/repo", min_samples=5)
        assert stats is None
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_is_outlier():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        store = ScoreStore(db_path=db_path)
        for i in range(10):
            store.record("owner/repo", i, slop_score=70, arch_score=70)

        result = store.is_outlier("owner/repo", 30, "slop", min_samples=5)
        assert result.is_outlier is True
        assert result.z_score < -1.5

        result = store.is_outlier("owner/repo", 70, "slop", min_samples=5)
        assert result.is_outlier is False
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_recent_analyses():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        store = ScoreStore(db_path=db_path)
        store.record("owner/repo", 1, slop_score=50, arch_score=60)
        store.record("owner/repo", 2, slop_score=30, arch_score=40)

        analyses = store.recent_analyses(limit=10)
        assert len(analyses) == 2
        assert analyses[0]["pr_number"] == 2
        assert analyses[0]["slop_score"] == 30
    finally:
        Path(db_path).unlink(missing_ok=True)

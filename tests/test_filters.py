from pullguard.config import PullGuardConfig
from pullguard.filters import DiffFilter
from pullguard.models import PRFile


def test_below_min_lines_skips():
    config = PullGuardConfig()
    config.analysis.min_lines_changed = 10
    f = DiffFilter(config)
    files = [PRFile(filename="test.py", status="modified", additions=3, deletions=2)]
    result = f.evaluate(files)
    assert result.should_skip is True
    assert result.reason == "below_min_diff"


def test_above_min_lines_passes():
    config = PullGuardConfig()
    config.analysis.min_lines_changed = 10
    f = DiffFilter(config)
    files = [PRFile(filename="test.py", status="modified", additions=8, deletions=5)]
    result = f.evaluate(files)
    assert result.should_skip is False


def test_skip_patterns_filtered():
    config = PullGuardConfig()
    config.analysis.min_lines_changed = 5
    f = DiffFilter(config)
    files = [
        PRFile(filename="README.md", status="modified", additions=100, deletions=0),
    ]
    result = f.evaluate(files)
    assert result.should_skip is True
    assert result.reason == "only_skipped_files"


def test_mixed_files():
    config = PullGuardConfig()
    config.analysis.min_lines_changed = 5
    f = DiffFilter(config)
    files = [
        PRFile(filename="README.md", status="modified", additions=100, deletions=0),
        PRFile(filename="src/main.py", status="modified", additions=5, deletions=0),
    ]
    result = f.evaluate(files)
    assert result.should_skip is False
    assert result.files_filtered == 1

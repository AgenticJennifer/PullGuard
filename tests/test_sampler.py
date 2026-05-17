from pullguard.config import PullGuardConfig
from pullguard.sampler import FileSampler
from pullguard.models import PRFile


def test_no_sampling_needed():
    config = PullGuardConfig()
    config.analysis.max_files_to_sample = 10
    s = FileSampler(config)
    files = [PRFile(filename=f"test_{i}.py", status="modified", additions=1, deletions=0) for i in range(5)]
    result = s.sample(files)
    assert result.sampled_count == 5
    assert result.strategy_used == "none_needed"


def test_priority_sampling():
    config = PullGuardConfig()
    config.analysis.max_files_to_sample = 2
    config.architect.required_dirs = ["src/"]
    s = FileSampler(config)
    files = [
        PRFile(filename="README.md", status="modified", additions=1, deletions=0),
        PRFile(filename="src/core.py", status="modified", additions=100, deletions=0),
        PRFile(filename="tests/test_main.py", status="modified", additions=50, deletions=0),
    ]
    result = s.sample(files)
    assert result.sampled_count == 2
    assert result.files[0].filename == "src/core.py"
    assert result.strategy_used == "priority"


def test_truncate_strategy():
    config = PullGuardConfig()
    config.analysis.max_files_to_sample = 2
    config.analysis.sampling_strategy = "truncate"
    s = FileSampler(config)
    files = [PRFile(filename=f"test_{i}.py", status="modified", additions=1, deletions=0) for i in range(10)]
    result = s.sample(files)
    assert result.sampled_count == 2
    assert result.files[0].filename == "test_0.py"
    assert result.strategy_used == "truncate"


def test_sampler_metadata():
    config = PullGuardConfig()
    config.analysis.max_files_to_sample = 3
    s = FileSampler(config)
    files = [PRFile(filename=f"test_{i}.py", status="modified", additions=1, deletions=0) for i in range(10)]
    result = s.sample(files)
    assert result.total_files == 10
    assert result.sampled_count == 3

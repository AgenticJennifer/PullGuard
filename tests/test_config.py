from pathlib import Path
import tempfile
import yaml
from pullguard.config import PullGuardConfig


def test_default_config():
    config = PullGuardConfig()
    assert config.analysis.min_score == 50
    assert config.llm.model == "gemini-2.0-flash"


def test_config_from_file():
    data = {
        "version": 1,
        "analysis": {"min_score": 70},
        "llm": {"model": "gemini-2.0-pro"},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(data, f)
        fname = f.name
    config = PullGuardConfig.from_file(fname)
    assert config.analysis.min_score == 70
    assert config.llm.model == "gemini-2.0-pro"
    Path(fname).unlink()


def test_from_file_missing():
    config = PullGuardConfig.from_file("/tmp/does_not_exist_xyz.yml")
    assert config.analysis.min_score == 50

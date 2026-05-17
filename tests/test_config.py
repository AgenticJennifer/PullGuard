from pathlib import Path
import tempfile
import yaml
from pullguard.config import PullGuardConfig


def test_default_config():
    config = PullGuardConfig()
    assert config.llm.model == "gemini-2.0-flash"
    assert config.analysis.min_scores == {"slop": 25, "arch": 40}
    assert config.analysis.sampling_strategy == "priority"
    assert config.slop_classifier.thresholds.suspicious == 40
    assert config.slop_classifier.thresholds.likely_slop == 25
    assert config.architect.thresholds.minor_violations == 60
    assert config.architect.thresholds.major_violations == 40


def test_config_from_file():
    data = {
        "version": 1,
        "analysis": {"min_scores": {"slop": 30, "arch": 50}},
        "llm": {"model": "gemini-2.0-pro", "provider": "gemini"},
        "slop_classifier": {"thresholds": {"suspicious": 50, "likely_slop": 30}},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(data, f)
        fname = f.name
    config = PullGuardConfig.from_file(fname)
    assert config.analysis.min_scores == {"slop": 30, "arch": 50}
    assert config.llm.model == "gemini-2.0-pro"
    assert config.llm.provider == "gemini"
    assert config.slop_classifier.thresholds.suspicious == 50
    assert config.slop_classifier.thresholds.likely_slop == 30
    Path(fname).unlink()


def test_from_file_missing():
    config = PullGuardConfig.from_file("/tmp/does_not_exist_xyz.yml")
    assert config.llm.model == "gemini-2.0-flash"

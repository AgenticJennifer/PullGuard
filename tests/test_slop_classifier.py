from pullguard.models import PullRequest, PRFile, SlopCategory
from pullguard.config import PullGuardConfig
from pullguard.agents.slop_classifier import SlopClassifier


def test_parse_response():
    classifier = SlopClassifier(PullGuardConfig())
    text = '{"score": 85, "category": "real", "reasoning": "Looks good", "signals": ["clean"], "red_flags": []}'
    result = classifier._parse_response(text)
    assert result["score"] == 85
    assert result["category"] == "real"


def test_format_files_truncates_long_patches():
    classifier = SlopClassifier(PullGuardConfig())
    pr = PullRequest(
        number=1, title="t", author="a", base_branch="main",
        head_sha="abc", url="https://github.com/a/b/pull/1",
        files=[PRFile(filename="test.py", status="modified", additions=1000, deletions=0, patch="a" * 2000)]
    )
    result = classifier._format_files(pr)
    assert len(result) < 2500  # truncated


def test_parse_response_fallback():
    classifier = SlopClassifier(PullGuardConfig())
    result = classifier._parse_response("not json at all")
    assert result["score"] == 50
    assert result["category"] == "suspicious"

from pullguard.models import PullRequest, SlopAnalysis, SlopCategory
from pullguard.config import PullGuardConfig
from pullguard.agents.liaison import CommunityLiaison


def test_format_findings_empty():
    liaison = CommunityLiaison(PullGuardConfig())
    assert liaison._format_findings(None) == "(no findings)"


def test_parse_response():
    liaison = CommunityLiaison(PullGuardConfig())
    text = '{"body": "Great PR!", "tone": "praise", "include_summary": true, "include_score": true, "inline_comments": []}'
    result = liaison._parse_response(text)
    assert result["body"] == "Great PR!"
    assert result["tone"] == "praise"


def test_parse_response_fallback():
    liaison = CommunityLiaison(PullGuardConfig())
    result = liaison._parse_response("bad data")
    assert "Thank you" in result["body"]

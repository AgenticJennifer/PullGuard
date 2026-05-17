from pullguard.models import PullRequest, PRFile
from pullguard.config import PullGuardConfig
from pullguard.agents.architect import ArchitectureAuditor


def test_parse_response():
    auditor = ArchitectureAuditor(PullGuardConfig())
    text = '{"passed": true, "score": 90, "findings": [], "project_docs_used": ["README.md"]}'
    result = auditor._parse_response(text)
    assert result["passed"] is True
    assert result["score"] == 90


def test_load_project_docs_no_dir():
    auditor = ArchitectureAuditor(PullGuardConfig())
    result = auditor._load_project_docs("/tmp/nonexistent_dir_xyz_abc")
    assert "(no project docs found)" in result


def test_parse_response_fallback():
    auditor = ArchitectureAuditor(PullGuardConfig())
    result = auditor._parse_response("garbage text")
    assert result["passed"] is False
    assert result["score"] == 50

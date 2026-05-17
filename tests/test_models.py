from pullguard.models import SlopAnalysis, SlopCategory, ArchitectureAudit, ArchitectureFinding


def test_slop_score_bounds():
    s = SlopAnalysis(score=50, category=SlopCategory.SUSPICIOUS, reasoning="test")
    assert 0 <= s.score <= 100


def test_architecture_scoring():
    findings = [
        ArchitectureFinding(severity="error", message="bad"),
        ArchitectureFinding(severity="warning", message="eh"),
    ]
    audit = ArchitectureAudit(passed=False, score=40, findings=findings)
    assert audit.score == 40
    assert audit.passed is False

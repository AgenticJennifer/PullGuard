from pullguard.models import PullRequest, SlopAnalysis, SlopCategory, ArchitectureAudit
from pullguard.config import PullGuardConfig
from pullguard.director import Director


def test_compute_score_both():
    config = PullGuardConfig()
    director = Director(config)
    slop = SlopAnalysis(score=80, category=SlopCategory.REAL, reasoning="good")
    arch = ArchitectureAudit(passed=True, score=90)
    score = director._compute_score(slop, arch)
    assert score == 85


def test_compute_score_slop_only():
    config = PullGuardConfig()
    director = Director(config)
    slop = SlopAnalysis(score=60, category=SlopCategory.SUSPICIOUS, reasoning="meh")
    score = director._compute_score(slop, None)
    assert score == 60


def test_compute_score_none():
    config = PullGuardConfig()
    director = Director(config)
    score = director._compute_score(None, None)
    assert score == 0


def test_director_init():
    config = PullGuardConfig()
    director = Director(config)
    assert director.slop_classifier is not None
    assert director.architect is not None
    assert director.liaison is not None

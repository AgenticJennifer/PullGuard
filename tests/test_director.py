from pullguard.models import PullRequest, SlopAnalysis, SlopCategory, ArchitectureAudit
from pullguard.config import PullGuardConfig
from pullguard.director import Director


def test_is_flagged_below_slop_threshold():
    config = PullGuardConfig()
    director = Director(config)
    slop = SlopAnalysis(score=20, category=SlopCategory.LIKELY_SLOP, reasoning="bad")
    arch = ArchitectureAudit(passed=True, score=90)
    assert director._is_flagged(slop, arch) is True


def test_is_flagged_below_arch_threshold():
    config = PullGuardConfig()
    director = Director(config)
    slop = SlopAnalysis(score=80, category=SlopCategory.REAL, reasoning="good")
    arch = ArchitectureAudit(passed=False, score=30)
    assert director._is_flagged(slop, arch) is True


def test_is_flagged_not_flagged():
    config = PullGuardConfig()
    director = Director(config)
    slop = SlopAnalysis(score=80, category=SlopCategory.REAL, reasoning="good")
    arch = ArchitectureAudit(passed=True, score=80)
    assert director._is_flagged(slop, arch) is False


def test_is_flagged_none():
    config = PullGuardConfig()
    director = Director(config)
    assert director._is_flagged(None, None) is False


def test_director_init():
    config = PullGuardConfig()
    director = Director(config)
    assert director.slop_classifier is not None
    assert director.architect is not None
    assert director.liaison is not None

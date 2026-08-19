from app.services.scoring_service import ScoringService


def test_scoring_perfect_clean_code():
    scores = ScoringService.calculate_scores([])
    assert scores["overall_score"] == 100.0
    assert scores["security_score"] == 100.0
    assert scores["quality_score"] == 100.0
    assert scores["performance_score"] == 100.0
    assert scores["maintainability_score"] == 100.0


def test_scoring_penalties():
    findings = [
        {"severity": "CRITICAL", "category": "security"},
        {"severity": "HIGH", "category": "bug"},
        {"severity": "MEDIUM", "category": "performance"},
        {"severity": "LOW", "category": "quality"},
    ]
    scores = ScoringService.calculate_scores(findings)
    assert scores["overall_score"] < 80.0
    assert scores["security_score"] < 80.0
    assert scores["quality_score"] < 90.0
    assert scores["performance_score"] < 95.0
    assert 0.0 <= scores["overall_score"] <= 100.0


def test_scoring_clamping():
    # 10 critical issues should clamp at 0.0, not go negative
    findings = [{"severity": "CRITICAL", "category": "security"}] * 10
    scores = ScoringService.calculate_scores(findings)
    assert scores["overall_score"] == 0.0
    assert scores["security_score"] == 0.0

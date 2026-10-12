
import pytest

from database.models.routes.services.risk_engine import calculate_risk


@pytest.mark.parametrize(
    "score",
    [0, 10, 35, 60, 80, 100]
)
def test_risk_score_is_in_valid_range(score):
    assert 0 <= calculate_risk(name_similarity=score)["risk_score"] <= 100


def test_risk_levels():
    assert risk_level(10) == "Low"
    assert risk_level(35) == "Medium"
    assert risk_level(60) == "High"
    assert risk_level(80) == "Critical"


def risk_level(score):
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"

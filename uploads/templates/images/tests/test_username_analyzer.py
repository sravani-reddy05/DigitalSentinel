
import pytest

from database.models.routes.services.username_analyzer import analyze_username


def test_exact_brand_username():
    result = analyze_username("adidas", "adidas")
    assert result["contains_brand"] is True
    assert result["lookalike_detected"] is False


def test_lookalike_username():
    result = analyze_username("adidazsupport_help", "adidas")
    assert result["lookalike_detected"] is True
    assert result["similarity"] >= 55


def test_username_containing_brand_is_not_flagged_as_lookalike():
    result = analyze_username("adidassupport_help", "adidas")
    assert result["contains_brand"] is True
    assert result["lookalike_detected"] is False


def test_unrelated_username():
    result = analyze_username("gardenflowers123", "adidas")
    assert result["lookalike_detected"] is False


def test_lookalike_name_with_digit_substitutions():
    result = analyze_username("g00gle_support", "Google")
    assert result["lookalike_detected"] is True
    assert result["similarity"] == 100


def test_lookalike_name_with_unicode_confusables():
    result = analyze_username("pаypal_support", "PayPal")
    assert result["lookalike_detected"] is True
    assert result["visually_confusable"] is True
    assert result["similarity"] == 100


def test_empty_username():
    assert analyze_username("", "adidas")["similarity"] == 0

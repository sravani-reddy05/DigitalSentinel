
import pytest

from database.models.routes.services.username_analyzer import analyze_username


def test_exact_brand_username():
    result = analyze_username("adidas", "adidas")
    assert result is not None


def test_lookalike_username():
    result = analyze_username("adidassupport_help", "adidas")
    assert result is not None


def test_unrelated_username():
    result = analyze_username("gardenflowers123", "adidas")
    assert result is not None


def test_empty_username():
    assert analyze_username("", "adidas")["similarity"] == 0

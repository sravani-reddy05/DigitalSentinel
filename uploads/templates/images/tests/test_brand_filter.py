
from database.models.routes.services.official_asset_filter import is_approved_asset


def test_asset_must_be_registered_and_approved():
    # Asset verification is backed by the configured database, not a filename check.
    assert is_approved_asset(999999, "logo", "Other", "brand.png") is False

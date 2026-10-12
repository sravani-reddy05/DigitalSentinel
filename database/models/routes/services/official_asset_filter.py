
from database.models.brand_model import get_official_assets


def is_approved_asset(
    brand_id,
    asset_type,
    platform,
    asset_name,
    asset_url=""
):
    assets = get_official_assets(brand_id)

    name_to_match = str(asset_name or "").strip().lower()
    url_to_match = str(asset_url or "").strip().rstrip("/").lower()
    platform_to_match = str(platform or "").strip().lower()
    type_to_match = str(asset_type or "").strip().lower()

    for asset in assets:
        if not asset.get("verified"):
            continue

        if str(asset.get("asset_type", "")).lower() != type_to_match:
            continue

        if str(asset.get("platform", "")).lower() != platform_to_match:
            continue

        stored_name = str(asset.get("asset_name", "")).strip().lower()
        stored_url = str(asset.get("asset_url", "")).strip().rstrip("/").lower()

        if name_to_match and name_to_match == stored_name:
            return True

        if url_to_match and url_to_match == stored_url:
            return True

    return False

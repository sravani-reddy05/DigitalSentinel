
import os


def get_source_status():
    """Report configuration status without exposing secret values."""

    instagram_configured = bool(
        os.getenv("INSTAGRAM_ACCESS_TOKEN")
        and os.getenv("INSTAGRAM_USER_ID")
    )

    facebook_configured = bool(
        os.getenv("FACEBOOK_ACCESS_TOKEN")
        and os.getenv("FACEBOOK_PAGE_ID")
    )

    google_play_configured = bool(
        os.getenv("GOOGLE_PLAY_API_ENABLED", "").lower() == "true"
    )

    app_store_configured = bool(
        os.getenv("APP_STORE_API_ENABLED", "").lower() == "true"
    )

    return {
        "instagram": {
            "configured": instagram_configured,
            "status": (
                "Credentials configured; API access still needs validation"
                if instagram_configured
                else "Not configured"
            ),
            "live_scanning_available": False
        },
        "facebook": {
            "configured": facebook_configured,
            "status": (
                "Credentials configured; API access still needs validation"
                if facebook_configured
                else "Not configured"
            ),
            "live_scanning_available": False
        },
        "google_play": {
            "configured": google_play_configured,
            "status": (
                "Integration flag enabled; endpoint and permissions "
                "must still be implemented"
                if google_play_configured
                else "Not configured"
            ),
            "live_scanning_available": False
        },
        "apple_app_store": {
            "configured": app_store_configured,
            "status": (
                "Integration flag enabled; endpoint and permissions "
                "must still be implemented"
                if app_store_configured
                else "Not configured"
            ),
            "live_scanning_available": False
        }
    }

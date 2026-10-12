
import os


class InstagramClient:
    """Placeholder for an approved Instagram API integration."""

    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.user_id = os.getenv("INSTAGRAM_USER_ID", "")

    def is_configured(self):
        return bool(self.access_token and self.user_id)

    def get_status(self):
        if not self.is_configured():
            return {
                "success": False,
                "source": "Instagram",
                "status": "Not configured",
                "message": (
                    "Configure the required credentials and obtain "
                    "the appropriate platform permissions."
                )
            }

        return {
            "success": False,
            "source": "Instagram",
            "status": "Not implemented",
            "message": (
                "Credentials are present, but live profile retrieval "
                "has not been implemented or validated."
            )
        }

    def search_profiles(self, query):
        """Do not imply arbitrary public-profile search is available."""
        query = str(query or "").strip()

        if not query:
            return {
                "success": False,
                "profiles": [],
                "error": "A search query is required."
            }

        return {
            "success": False,
            "profiles": [],
            "error": (
                "Live Instagram profile search is unavailable in this "
                "prototype. Use the manual-entry analysis endpoint."
            )
        }

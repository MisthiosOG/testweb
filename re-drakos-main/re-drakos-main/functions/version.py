from functions.version_live import get_version as get_version_live
from functions.version_beta import get_version as get_version_beta

FALLBACK_VERSION = "0.33.7.394009" # Keep the latest version as fallback


class Version:
    @staticmethod
    async def get_version(server_type):
        # Forcing to use FALLBACK_VERSION to ensure consistency with license.py hashes
        # If scraping is needed, this logic can be re-enabled.
        return FALLBACK_VERSION

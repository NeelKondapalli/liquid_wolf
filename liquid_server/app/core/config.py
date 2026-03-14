"""
Application configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Application
    APP_NAME = "Liquid Wolf Server"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # API Security
    API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key-change-in-production")

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    # Prefer SUPABASE_KEY if set, otherwise fallback to service role or publishable
    SUPABASE_KEY = (
        os.getenv("SUPABASE_KEY") or  # Direct key (set in .env)
        os.getenv("SUPABASE_SERVICE_ROLE_KEY") or  # Service role (for production)
        os.getenv("SUPABASE_PUBLISHABLE_KEY")  # Publishable (limited permissions)
    )

    # Liquid API
    LIQUID_BASE_URL = os.getenv(
        "LIQUID_BASE_URL",
        "https://api-public.liquidmax.xyz"
    )

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ["SUPABASE_URL", "SUPABASE_KEY", "API_SECRET_KEY"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")


# Validate on import
Config.validate()

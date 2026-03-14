"""
Supabase database service for user and API key management
"""
from supabase import create_client, Client
from typing import Optional, Tuple
from app.core.config import Config


class SupabaseService:
    """Service for interacting with Supabase database"""

    def __init__(self):
        """Initialize Supabase client"""
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )

    def check_user_exists(self, phone_number: str) -> bool:
        """
        Check if a user exists by phone number

        Args:
            phone_number: User's phone number

        Returns:
            True if user exists, False otherwise
        """
        try:
            response = self.client.table("users").select("phone_number").eq(
                "phone_number", phone_number
            ).execute()
            return len(response.data) > 0
        except Exception as e:
            raise Exception(f"Failed to check user existence: {str(e)}")

    def get_active_liquid_keys(
        self, phone_number: str
    ) -> Optional[Tuple[str, str]]:
        """
        Get active Liquid API credentials for a user

        Args:
            phone_number: User's phone number

        Returns:
            Tuple of (api_key, api_secret) if found and active, None otherwise
        """
        try:
            response = (
                self.client.table("liquid_keys")
                .select("api_key, api_secret")
                .eq("phone_number", phone_number)
                .eq("is_active", True)
                .execute()
            )

            if not response.data:
                return None

            key_data = response.data[0]
            return (key_data["api_key"], key_data["api_secret"])

        except Exception as e:
            raise Exception(f"Failed to fetch liquid keys: {str(e)}")

    def has_active_keys(self, phone_number: str) -> bool:
        """
        Check if user has active Liquid API keys

        Args:
            phone_number: User's phone number

        Returns:
            True if user has active keys, False otherwise
        """
        keys = self.get_active_liquid_keys(phone_number)
        return keys is not None

    def create_user(self, phone_number: str) -> bool:
        """
        Create a new user

        Args:
            phone_number: User's phone number

        Returns:
            True if successful
        """
        try:
            self.client.table("users").insert({
                "phone_number": phone_number
            }).execute()
            return True
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")

    def add_liquid_keys(
        self, phone_number: str, api_key: str, api_secret: str
    ) -> bool:
        """
        Add Liquid API keys for a user

        Args:
            phone_number: User's phone number
            api_key: Liquid API key
            api_secret: Liquid API secret

        Returns:
            True if successful
        """
        try:
            self.client.table("liquid_keys").insert({
                "phone_number": phone_number,
                "api_key": api_key,
                "api_secret": api_secret,
                "is_active": True
            }).execute()
            return True
        except Exception as e:
            raise Exception(f"Failed to add liquid keys: {str(e)}")

    def deactivate_liquid_keys(self, phone_number: str) -> bool:
        """
        Deactivate Liquid API keys for a user

        Args:
            phone_number: User's phone number

        Returns:
            True if successful
        """
        try:
            self.client.table("liquid_keys").update({
                "is_active": False
            }).eq("phone_number", phone_number).execute()
            return True
        except Exception as e:
            raise Exception(f"Failed to deactivate keys: {str(e)}")


# Global instance - initialized after imports
supabase_service = SupabaseService()

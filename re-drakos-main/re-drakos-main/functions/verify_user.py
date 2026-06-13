import aiohttp
import asyncio
import json

VERIFY_URL = 'https://devildrakos.com/api/drakos-tele-bot/check?format=json'


class VerifyUser:
    async def verify_user(self, telegram_id, telegram_username):
        """
        Verifies that a user is allowed to access the system.

        Args:
            telegram_id (str): The Telegram ID of the user.
            telegram_username (str): The Telegram username of the user.

        Returns:
            bool: True if the user is allowed, False otherwise.
        """
        payload = {
            "searchNumber": telegram_id,
            "username": telegram_username
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url=VERIFY_URL, json=payload) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data["result"] == "ok" and response_data["access"] == "allowed"
                    else:
                        return False
            except aiohttp.ClientError as e:
                error_msg = f"An error occurred while verifying user {telegram_id}: {e}"
                print(error_msg)
                return False

    async def register_user(self, telegram_id, telegram_username):
        """
        Registers a user in the system.

        Args:
            telegram_id (str): The Telegram ID of the user.
            telegram_username (str): The Telegram username of the user.

        Returns:
            str: The registration status of the user (allowed, denied, registered, pending), or False on error.
        """
        payload = {
            "searchNumber": telegram_id,
            "username": telegram_username
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url=VERIFY_URL, json=payload) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        result = response_data["result"]

                        if result == "ok":
                            access = response_data["access"]
                            if access == "allowed":
                                return "allowed"
                            elif access == "deny":
                                return "denied"
                            else:
                                # This should not happen, but return False just in case
                                return False
                        elif result == "done_regist":
                            return "registered"
                        elif result == "already_regist":
                            return "pending"
                        else:
                            # Unknown result code
                            return False
                    else:
                        return False
            except aiohttp.ClientError as e:
                error_msg = f"An error occurred while registering user {telegram_id}: {e}"
                print(error_msg)
                return False

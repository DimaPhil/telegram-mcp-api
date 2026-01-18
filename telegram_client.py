"""
Telegram Client - Python client library for local scripts.

This client connects to the Telegram HTTP API running in Docker
and provides a simple interface for Telegram operations.

Usage:
    from telegram_client import TelegramClient

    client = TelegramClient()  # Defaults to http://localhost:8080

    # Get chats
    chats = client.get_chats()

    # Send a message
    client.send_message(chat_id=123456789, message="Hello!")
"""

import json
from typing import Optional, List, Union, Any, Dict
import httpx


class TelegramClientError(Exception):
    """Exception raised for Telegram API errors."""
    pass


class TelegramClient:
    """Client for interacting with the Telegram HTTP API."""

    def __init__(self, base_url: str = "http://localhost:8080", timeout: float = 30.0):
        """
        Initialize the Telegram client.

        Args:
            base_url: The base URL of the Telegram API server.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
    ) -> Any:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"

        response = self._client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
        )
        response.raise_for_status()

        result = response.json()

        if not result.get("success"):
            raise TelegramClientError(result.get("error", "Unknown error"))

        data = result.get("data")
        if data:
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return data
        return data

    def _get(self, endpoint: str, **params) -> Any:
        """Make a GET request."""
        return self._request("GET", endpoint, params=params)

    def _post(self, endpoint: str, **data) -> Any:
        """Make a POST request."""
        return self._request("POST", endpoint, json_data=data)

    def _put(self, endpoint: str, **data) -> Any:
        """Make a PUT request."""
        return self._request("PUT", endpoint, json_data=data)

    def _delete(self, endpoint: str, **data) -> Any:
        """Make a DELETE request."""
        if data:
            return self._request("DELETE", endpoint, json_data=data)
        return self._request("DELETE", endpoint)

    # ==================== Health Check ====================

    def health_check(self) -> Dict:
        """Check if the API is healthy."""
        response = self._client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    # ==================== Chat Operations ====================

    def get_chats(self, page: int = 1, page_size: int = 20) -> str:
        """Get a paginated list of chats."""
        return self._get("/chats", page=page, page_size=page_size)

    def list_chats(
        self,
        limit: int = 50,
        chat_type: Optional[str] = None,
        archived: bool = False,
        unread_only: bool = False,
    ) -> List[Dict]:
        """Get a filtered list of chats with metadata."""
        params = {"limit": limit, "archived": archived, "unread_only": unread_only}
        if chat_type:
            params["chat_type"] = chat_type
        return self._get("/chats/list", **params)

    def get_chat(self, chat_id: Union[int, str]) -> Dict:
        """Get detailed information about a specific chat."""
        return self._get(f"/chats/{chat_id}")

    # ==================== Message Operations ====================

    def get_messages(
        self, chat_id: Union[int, str], page: int = 1, page_size: int = 20
    ) -> str:
        """Get paginated messages from a chat."""
        return self._get(f"/chats/{chat_id}/messages", page=page, page_size=page_size)

    def send_message(
        self,
        chat_id: Union[int, str],
        message: str,
        reply_to: Optional[int] = None,
        parse_mode: Optional[str] = None,
    ) -> str:
        """Send a message to a chat."""
        data = {"chat_id": chat_id, "message": message}
        if reply_to:
            data["reply_to"] = reply_to
        if parse_mode:
            data["parse_mode"] = parse_mode
        return self._post("/messages/send", **data)

    def edit_message(
        self, chat_id: Union[int, str], message_id: int, new_text: str
    ) -> str:
        """Edit an existing message."""
        return self._put(
            "/messages/edit",
            chat_id=chat_id,
            message_id=message_id,
            new_text=new_text,
        )

    def delete_message(
        self, chat_id: Union[int, str], message_id: int, revoke: bool = True
    ) -> str:
        """Delete a message."""
        return self._delete(
            "/messages/delete",
            chat_id=chat_id,
            message_id=message_id,
            revoke=revoke,
        )

    def forward_message(
        self, from_chat_id: Union[int, str], to_chat_id: Union[int, str], message_id: int
    ) -> str:
        """Forward a message from one chat to another."""
        return self._post(
            "/messages/forward",
            from_chat_id=from_chat_id,
            to_chat_id=to_chat_id,
            message_id=message_id,
        )

    def search_messages(
        self,
        chat_id: Union[int, str],
        query: str,
        limit: int = 20,
        from_user: Optional[Union[int, str]] = None,
    ) -> List[Dict]:
        """Search for messages in a chat."""
        data = {"chat_id": chat_id, "query": query, "limit": limit}
        if from_user:
            data["from_user"] = from_user
        return self._post("/messages/search", **data)

    # ==================== Contact Operations ====================

    def list_contacts(self) -> List[Dict]:
        """Get all contacts."""
        return self._get("/contacts")

    def search_contacts(self, query: str, limit: int = 10) -> List[Dict]:
        """Search contacts by name or username."""
        return self._get("/contacts/search", query=query, limit=limit)

    def add_contact(
        self, phone: str, first_name: str, last_name: Optional[str] = None
    ) -> str:
        """Add a new contact."""
        data = {"phone": phone, "first_name": first_name}
        if last_name:
            data["last_name"] = last_name
        return self._post("/contacts", **data)

    def delete_contact(self, user_id: Union[int, str]) -> str:
        """Delete a contact."""
        return self._delete(f"/contacts/{user_id}")

    # ==================== User Operations ====================

    def get_me(self) -> Dict:
        """Get information about the current user."""
        return self._get("/me")

    def get_user_status(self, user_id: Union[int, str]) -> Dict:
        """Get the online status of a user."""
        return self._get(f"/users/{user_id}/status")

    def resolve_username(self, username: str) -> Dict:
        """Resolve a username to get entity information."""
        return self._get(f"/resolve/{username}")

    # ==================== Group Operations ====================

    def create_group(self, title: str, users: List[Union[int, str]]) -> str:
        """Create a new group chat."""
        return self._post("/groups", title=title, users=users)

    def invite_to_group(
        self, chat_id: Union[int, str], user_ids: List[Union[int, str]]
    ) -> str:
        """Invite users to a group or channel."""
        return self._post("/groups/invite", chat_id=chat_id, user_ids=user_ids)

    def leave_chat(self, chat_id: Union[int, str]) -> str:
        """Leave a group or channel."""
        return self._post(f"/chats/{chat_id}/leave")

    def get_participants(
        self, chat_id: Union[int, str], limit: int = 100, offset: int = 0
    ) -> List[Dict]:
        """Get participants of a group or channel."""
        return self._get(f"/chats/{chat_id}/participants", limit=limit, offset=offset)

    # ==================== Admin Operations ====================

    def get_admins(self, chat_id: Union[int, str]) -> List[Dict]:
        """Get administrators of a chat."""
        return self._get(f"/chats/{chat_id}/admins")

    def promote_admin(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str],
        title: Optional[str] = None,
    ) -> str:
        """Promote a user to admin."""
        data = {"chat_id": chat_id, "user_id": user_id}
        if title:
            data["title"] = title
        return self._post("/admin/promote", **data)

    def ban_user(
        self,
        chat_id: Union[int, str],
        user_id: Union[int, str],
        until_date: Optional[int] = None,
    ) -> str:
        """Ban a user from a chat."""
        data = {"chat_id": chat_id, "user_id": user_id}
        if until_date:
            data["until_date"] = until_date
        return self._post("/admin/ban", **data)

    def unban_user(self, chat_id: Union[int, str], user_id: Union[int, str]) -> str:
        """Unban a user from a chat."""
        return self._post("/admin/unban", chat_id=chat_id, user_id=user_id)

    # ==================== Channel Operations ====================

    def get_invite_link(self, chat_id: Union[int, str]) -> str:
        """Get the invite link for a chat."""
        return self._get(f"/chats/{chat_id}/invite-link")

    # ==================== Notification Operations ====================

    def mute_chat(
        self, chat_id: Union[int, str], mute_until: Optional[int] = None
    ) -> str:
        """Mute notifications for a chat."""
        params = {}
        if mute_until:
            params["mute_until"] = mute_until
        return self._post(f"/chats/{chat_id}/mute", **params)

    def unmute_chat(self, chat_id: Union[int, str]) -> str:
        """Unmute notifications for a chat."""
        return self._post(f"/chats/{chat_id}/unmute")

    # ==================== Archive Operations ====================

    def archive_chat(self, chat_id: Union[int, str]) -> str:
        """Archive a chat."""
        return self._post(f"/chats/{chat_id}/archive")

    def unarchive_chat(self, chat_id: Union[int, str]) -> str:
        """Unarchive a chat."""
        return self._post(f"/chats/{chat_id}/unarchive")

    # ==================== Draft Operations ====================

    def save_draft(
        self, chat_id: Union[int, str], message: str, reply_to: Optional[int] = None
    ) -> str:
        """Save a draft message to a chat."""
        data = {"chat_id": chat_id, "message": message}
        if reply_to:
            data["reply_to"] = reply_to
        return self._post("/drafts/save", **data)

    def clear_draft(self, chat_id: Union[int, str]) -> str:
        """Clear a draft from a chat."""
        return self._delete(f"/drafts/{chat_id}")


# Convenience function for quick usage
def get_client(base_url: str = "http://localhost:8080") -> TelegramClient:
    """Get a Telegram client instance."""
    return TelegramClient(base_url=base_url)

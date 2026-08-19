from typing import List, Optional, Dict, Any


class UserRecordManager:
    """Clean, well-structured Python class following PEP 8 conventions."""

    def __init__(self, initial_records: Optional[List[Dict[str, Any]]] = None) -> None:
        self.records: List[Dict[str, Any]] = initial_records if initial_records is not None else []

    def add_user(self, user_id: str, email: str, role: str = "member") -> Dict[str, Any]:
        """Add a new user record safely."""
        record = {
            "id": user_id,
            "email": email.strip().lower(),
            "role": role,
            "is_active": True
        }
        self.records.append(record)
        return record

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Lookup user record by email address."""
        target_email = email.strip().lower()
        for user in self.records:
            if user.get("email") == target_email:
                return user
        return None

    def get_active_user_count(self) -> int:
        """Return the number of active users in the system."""
        return sum(1 for user in self.records if user.get("is_active"))

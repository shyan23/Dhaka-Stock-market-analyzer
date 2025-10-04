"""
Session Token Manager
Implements JWT-like token system for session identification
"""

import hashlib
import secrets
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class SessionToken:
    """JWT-like session token for user sessions"""

    def __init__(self, token_string: str = None):
        if token_string:
            self.token = token_string
            self.payload = self._decode(token_string)
        else:
            self.token = None
            self.payload = {}

    @staticmethod
    def generate(username: str, session_data: Dict[str, Any] = None) -> 'SessionToken':
        """Generate a new session token for a user"""
        # Create unique session ID
        session_id = secrets.token_urlsafe(32)

        # Create timestamp
        issued_at = int(time.time())
        expires_at = issued_at + (30 * 24 * 60 * 60)  # 30 days

        # Build payload
        payload = {
            'session_id': session_id,
            'username': username,
            'issued_at': issued_at,
            'expires_at': expires_at,
            'data': session_data or {}
        }

        # Create token string (simple encoding - not cryptographically secure like real JWT)
        # Format: session_id.username.timestamp.signature
        token_string = SessionToken._encode(payload)

        token = SessionToken()
        token.token = token_string
        token.payload = payload
        return token

    @staticmethod
    def _encode(payload: Dict[str, Any]) -> str:
        """Encode payload into token string"""
        # Convert payload to JSON
        payload_json = json.dumps(payload, sort_keys=True)

        # Create signature using SHA256
        signature = hashlib.sha256(payload_json.encode()).hexdigest()[:16]

        # Encode payload as base64-like string (URL safe)
        import base64
        encoded_payload = base64.urlsafe_b64encode(payload_json.encode()).decode()

        # Format: encoded_payload.signature
        return f"{encoded_payload}.{signature}"

    @staticmethod
    def _decode(token_string: str) -> Dict[str, Any]:
        """Decode token string into payload"""
        try:
            parts = token_string.split('.')
            if len(parts) != 2:
                return {}

            encoded_payload, signature = parts

            # Decode payload
            import base64
            payload_json = base64.urlsafe_b64decode(encoded_payload.encode()).decode()
            payload = json.loads(payload_json)

            # Verify signature
            expected_signature = hashlib.sha256(payload_json.encode()).hexdigest()[:16]
            if signature != expected_signature:
                print("Warning: Token signature mismatch")
                return {}

            return payload
        except Exception as e:
            print(f"Error decoding token: {e}")
            return {}

    def is_valid(self) -> bool:
        """Check if token is valid and not expired"""
        if not self.payload:
            return False

        # Check expiration
        expires_at = self.payload.get('expires_at', 0)
        if time.time() > expires_at:
            return False

        return True

    def get_session_id(self) -> str:
        """Get session ID from token"""
        return self.payload.get('session_id', '')

    def get_username(self) -> str:
        """Get username from token"""
        return self.payload.get('username', '')

    def get_redis_key(self, key_suffix: str = '') -> str:
        """Get Redis key for this session"""
        session_id = self.get_session_id()
        if key_suffix:
            return f"session_{session_id}_{key_suffix}"
        return f"session_{session_id}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary"""
        return {
            'token': self.token,
            'session_id': self.get_session_id(),
            'username': self.get_username(),
            'issued_at': self.payload.get('issued_at'),
            'expires_at': self.payload.get('expires_at'),
            'valid': self.is_valid()
        }

    def __str__(self) -> str:
        return self.token or ''

    def __repr__(self) -> str:
        return f"SessionToken(session_id={self.get_session_id()}, username={self.get_username()}, valid={self.is_valid()})"


class SessionTokenManager:
    """Manages session tokens and their lifecycle"""

    def __init__(self, data_manager=None):
        self.data_manager = data_manager

    def create_session(self, username: str) -> SessionToken:
        """Create a new session for a user"""
        token = SessionToken.generate(username)

        # Store token in Redis if data_manager is available
        if self.data_manager:
            try:
                # Store token metadata
                token_key = f"user_{username}_session_token"
                self.data_manager.redis_client.setex(
                    token_key,
                    30 * 24 * 60 * 60,  # 30 days
                    token.token
                )

                # Store session metadata
                session_key = f"session_{token.get_session_id()}_metadata"
                metadata = {
                    'username': username,
                    'created_at': token.payload.get('issued_at'),
                    'expires_at': token.payload.get('expires_at')
                }
                self.data_manager.redis_client.setex(
                    session_key,
                    30 * 24 * 60 * 60,
                    json.dumps(metadata)
                )
            except Exception as e:
                print(f"Error storing session token: {e}")

        return token

    def get_session(self, username: str) -> Optional[SessionToken]:
        """Get existing session for a user"""
        if not self.data_manager:
            return None

        try:
            token_key = f"user_{username}_session_token"
            token_string = self.data_manager.redis_client.get(token_key)

            if token_string:
                if isinstance(token_string, bytes):
                    token_string = token_string.decode('utf-8')

                token = SessionToken(token_string)
                if token.is_valid():
                    return token
                else:
                    # Token expired, clean up
                    self.invalidate_session(username)
        except Exception as e:
            print(f"Error retrieving session token: {e}")

        return None

    def get_or_create_session(self, username: str) -> SessionToken:
        """Get existing session or create a new one"""
        token = self.get_session(username)
        if token and token.is_valid():
            return token
        return self.create_session(username)

    def invalidate_session(self, username: str):
        """Invalidate a user's session"""
        if not self.data_manager:
            return

        try:
            # Get current token to clean up session data
            token = self.get_session(username)
            if token:
                session_id = token.get_session_id()
                # Delete session metadata
                session_key = f"session_{session_id}_metadata"
                self.data_manager.redis_client.delete(session_key)

            # Delete user's token
            token_key = f"user_{username}_session_token"
            self.data_manager.redis_client.delete(token_key)
        except Exception as e:
            print(f"Error invalidating session: {e}")

    def validate_token(self, token: SessionToken) -> bool:
        """Validate a session token"""
        if not token or not token.is_valid():
            return False

        # Additional validation against Redis if needed
        if self.data_manager:
            try:
                session_key = f"session_{token.get_session_id()}_metadata"
                metadata = self.data_manager.redis_client.get(session_key)
                return metadata is not None
            except:
                pass

        return True

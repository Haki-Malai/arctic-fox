import pickle
import jwt
import secrets
from datetime import datetime, timedelta

from api.app import cache
from config import config


class Token:

    def __init__(self, user_id: int) -> None:
        """Create a new token for the given user

        param user_id: The user ID
        """
        self.user_id = user_id
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() + timedelta(
            minutes=config.ACCESS_TOKEN_MINUTES)
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = datetime.utcnow() + timedelta(
            days=config.REFRESH_TOKEN_DAYS)
        self.save()

    @property
    def access_token_jwt(self) -> str:
        """Return the access token as a JWT

        return: The access token as a JWT
        """
        return jwt.encode(
            {'token': self.access_token}, config.SECRET_KEY, algorithm='HS256')

    def save(self) -> None:
        """Save the token to Redis and register it."""
        token_data = pickle.dumps(self)
        cache.set(f'token:{self.access_token}', token_data,
                  timeout=config.REFRESH_TOKEN_DAYS * 24 * 3600)
        current_registry = cache.get('token_registry') or []
        current_registry.append(f'token:{self.access_token}')
        cache.set('token_registry', current_registry)

    def expire(self, delay: int=5) -> None:
        """Expire the token

        :param delay: The delay in seconds
        """
        self.access_expiration = datetime.utcnow() + timedelta(seconds=delay)
        self.refresh_expiration = datetime.utcnow() + timedelta(seconds=delay)
        self.save()

    @staticmethod
    def from_jwt(access_token_jwt: str) -> 'Token':
        """Return a token from a JWT

        :param access_token_jwt: The access token as a JWT

        :return: The token

        :raises ValueError: If the token is invalid or expired
        """
        decoded = jwt.decode(access_token_jwt, config.SECRET_KEY, algorithms=['HS256'])
        access_token = decoded.get('token')

        serialized_token = cache.get(f"token:{access_token}")

        if not serialized_token:
            raise ValueError("Invalid or expired token")

        token = pickle.loads(serialized_token)
        return token
    
    @staticmethod
    def clean() -> None:
        """Remove all expired tokens from the cache."""
        token_registry = cache.get('token_registry') or []
        for token_key in token_registry:
            serialized_token = cache.get(token_key)
            if serialized_token:
                token = pickle.loads(serialized_token)
                if token.access_expiration < datetime.utcnow() or token.refresh_expiration < datetime.utcnow():
                    cache.delete(token_key)
                    token_registry.remove(token_key)
        cache.set('token_registry', token_registry)

    @staticmethod
    def revoke_all(user_id: int) -> None:
        """Revoke all tokens for a given user ID.

        :param user_id: The user ID for which to revoke all tokens.
        """
        for key in cache.scan_iter(match='token:*'):
            serialized_token = cache.get(key)
            if serialized_token:
                token = pickle.loads(serialized_token)
                if token.user_id == user_id:
                    cache.delete(key)

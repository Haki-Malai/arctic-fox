import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from api.app import db
from api.email import send_email
from api.token import Token
from ..enums import Role
from ..mixins import TimestampMixin, UpdateableMixin

from typing import Optional


class User(TimestampMixin, UpdateableMixin, db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True)
    username: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64), unique=True)
    avatar_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    activated: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    role: so.Mapped[Role] = so.mapped_column(sa.Enum(Role), default=Role.VIEWER)

    folders = so.relationship('Folder', back_populates='owner')
    files = so.relationship('File', back_populates='owner')

    def __repr__(self) -> str:
        """Return a string representation of the user."""
        return '<User {}>'.format(self.username)

    def activate(self, idinfo: dict) -> None:
        """Activate the user with the given information.

        :param info: The information to activate the user with.
        """
        self.username = idinfo['name']
        self.avatar_url = idinfo['picture']
        self.activated = True

    def invite(self, email: str, role: str) -> Optional['User']:
        """Invite a user and create a new user.

        :param email: The email of the user to invite and create.
        :param role: The role of the user being invited as a string.

        :return: The new user.
        """
        try:
            user = User(email=email, role=role)
            db.session.add(user)
            db.session.commit()
            send_email(email, 'Invitation to Arctic Fox', 'invite', user_email=email)
            return user
        except IntegrityError:
            db.session.rollback()
            return

    def generate_auth_token(self) -> Token:
        """Generate a new access and refresh token."""
        return Token(self.id)

    @staticmethod
    def verify_access_token(access_token_jwt: str,
                            refresh_token: str = None) -> Optional['User']:
        """Return the user associated with the access token JWT.

        :param access_token_jwt: The access token JWT.
        :param refresh_token: The refresh token.

        :return: The user if the access token is valid, otherwise None.
        """
        token = Token.from_jwt(access_token_jwt)
        if token and token.access_expiration > datetime.utcnow():
            user = db.session.get(User, token.user_id)
            if user:
                db.session.commit()
            return user

    @staticmethod
    def verify_refresh_token(refresh_token: str,
                             access_token_jwt: str) -> Token|None:
        """Return the token associated with the refresh token.

        :param access_token_jwt: The access token JWT.
        :param refresh_token: The refresh token.

        :return: The token object
        """
        token = Token.from_jwt(access_token_jwt)
        if token and token.refresh_token == refresh_token:
            if token.refresh_expiration > datetime.utcnow():
                return token

            # Someone tried to refresh with an expired token
            # Revoke all tokens from this user as a precaution
            Token.revoke_all(token.user_id)
            db.session.commit()

    def revoke_all(self) -> None:
        """Revoke all tokens for the user."""
        Token.revoke_all(self.id)

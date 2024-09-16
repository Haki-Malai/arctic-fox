import enum


class Role(enum.Enum):
    ADMIN: int = 1
    MODERATOR: int = 2
    VIEWER: int = 3

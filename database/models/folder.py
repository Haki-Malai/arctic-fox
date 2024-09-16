import sqlalchemy as sa
import sqlalchemy.orm as so

from api.app import db
from ..mixins.timestamp import TimestampMixin, UpdateableMixin

from typing import Optional



class Folder(TimestampMixin, UpdateableMixin, db.Model):
    __tablename__ = 'folders'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(280))
    created_by: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))

    owner = so.relationship('User', back_populates='folders')
    files = so.relationship('File', back_populates='folder')

    def __repr__(self) -> str:
        """Return a string representation of the folder."""
        return f'<Folder {self.name}>'

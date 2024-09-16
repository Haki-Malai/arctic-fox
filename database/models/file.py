import sqlalchemy as sa
import sqlalchemy.orm as so

from api.app import db, celery
from ..mixins.timestamp import TimestampMixin, UpdateableMixin

from typing import Optional


class File(TimestampMixin, UpdateableMixin, db.Model):
    __tablename__ = 'files'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    filename: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    mimetype: so.Mapped[str] = so.mapped_column(sa.String(64))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(280))
    processed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    dominant_color: so.Mapped[Optional[str]] = so.mapped_column(sa.String(7))
    error: so.Mapped[Optional[str]] = so.mapped_column(sa.String(280))
    created_by: so.Mapped[int] = so.mapped_column(sa.ForeignKey('users.id'))
    folder_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('folders.id'))

    owner = so.relationship('User', back_populates='files')
    folder = so.relationship('Folder', back_populates='files')

    def __repr__(self) -> str:
        """Return a string representation of the file."""
        return f'<File {self.filename}>'


@sa.event.listens_for(File, 'after_insert')
def set_dominant_color(mapper, connection, target: File):
    celery.send_task('worker.tasks.file_tasks.set_dominant_color',
                     args=[target.id])


@sa.event.listens_for(File, 'before_delete')
def delete_s3_file(mapper, connection, target: File):
    """Delete file from S3 before deleting the record."""
    celery.send_task('worker.tasks.file_tasks.delete_s3_file',
                     args=[target.filename])

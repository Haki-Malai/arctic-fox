from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    @declared_attr
    def created_at(cls: type) -> Column:
        """Return a created_at column.

        :param cls: The class to create the column for.

        :return: The created_at column.
        """
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls: type) -> Column:
        """Return an updated_at column.

        :param cls: The class to create the column for.

        :return: The updated_at column.
        """
        return Column(
            DateTime,
            default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )

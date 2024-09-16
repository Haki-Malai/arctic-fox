class UpdateableMixin:
    def update(self, data: dict) -> None:
        """Update the object with the given data.

        :param data: The data to update the object with.
        """
        for attr, value in data.items():
            setattr(self, attr, value)

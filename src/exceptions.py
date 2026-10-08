class ResourceNotExistError(Exception):
    """Ресурс не найден."""

    def __init__(self, resource: str) -> None:
        super().__init__(f"{resource} not found")


class UnauthorizeError(Exception):
    """Ошибка идентификации."""


class DuplicatesIdempotencyKeyError(Exception):
    """Ключ идемпотентности дублирован."""

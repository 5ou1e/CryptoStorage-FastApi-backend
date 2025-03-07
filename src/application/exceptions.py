from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationException(Exception):
    """Base Error."""

    @property
    def title(self) -> str:
        return f"Ошибка приложения"

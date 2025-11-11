from abc import ABC, abstractmethod
from rich.console import Console


class AppException(Exception, ABC):
    @abstractmethod
    def display_message(self, console: Console) -> None:
        pass

    @abstractmethod
    def handle(self) -> None:
        pass

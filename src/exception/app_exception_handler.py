from src.exception.app_exception import AppException
from rich.console import Console


class AppExceptionHandler:
    def handle(self, exception: AppException):
        console = Console()
        exception.display_message(console)
        exception.handle()

import sys
from rich.console import Console
from src.exception.app_exception import AppException


class TaskNotSelectedException(AppException):
    def display_message(self, console: Console) -> None:
        console.print("[red]No task is currently selected.[/]")
        console.print(f"Please select a task using [italic]{sys.argv[0]} select[/]")

    def handle(self) -> None:
        sys.exit(1)


class TaskNotFoundException(AppException):
    def __init__(self, task_id: str):
        self.task_id = task_id

    def display_message(self, console: Console) -> None:
        console.print(f"[red]Task [bold]{self.task_id}[/] not found.[/]")
        console.print(f"Please select another task using [italic]{sys.argv[0]} select[/]")

    def handle(self) -> None:
        sys.exit(1)


class ConfigFileNotFoundException(AppException):
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path

    def display_message(self, console: Console) -> None:
        console.print(
            f"[red]Config file not found where expected ([italic]{self.config_file_path}[/italic])."
        )

    def handle(self) -> None:
        sys.exit(1)


class ConfigFileCannotBeParsedException(AppException):
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path

    def display_message(self, console: Console) -> None:
        console.print(
            f"[red]Error while parsing config file ([italic]{self.config_file_path}[/italic])."
        )

    def handle(self) -> None:
        sys.exit(1)

import sys
from rich.console import Console
from src.exception.app_exception import AppException


class TaskNotSelectedException(AppException):
    def display_message(self, console: Console) -> None:
        console.print("[red]No task is currently selected.[/]")
        console.print(f"Please select a task using [italic]{sys.argv[0]}[/] select")

    def handle(self) -> None:
        exit(1)


class TaskNotFoundException(AppException):
    def __init__(self, task_id: str):
        self.task_id = task_id

    def display_message(self, console: Console) -> None:
        console.print(f"[red]Task [bold]{self.task_id}[/] not found.[/]")
        console.print(f"Please select another task using [italic]{sys.argv[0]}[/]")

    def handle(self) -> None:
        exit(1)

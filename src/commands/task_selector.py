from rich import print
from src.api_manager import ApiManager
from src.config import Config
from src.model.task import TaskStateReadModel, TaskStatus
import questionary
from questionary import Choice
from prompt_toolkit.formatted_text import FormattedText


class TaskSelector:
    def __init__(self, config: Config, api: ApiManager):
        self.api = api
        self.config = config

    def run(self, task_id: str | None) -> None:
        if not task_id:
            task = self.__task_selector()
        else:
            task = self.api.get_task(task_id)

            if not task:
                print(f"Task with ID {task_id} not found.")

        self.config.state.current_task = task.id
        print(f"Task {task.id} selected!")

    def __task_selector(self) -> TaskStateReadModel:
        tasks_list = self.api.get_task_list(self.config.state.current_course)

        choices = []
        suggested = None
        for task in tasks_list:
            text = []

            text.append(("gray italic", f"{task.orderId}"))
            text.append(("", ".  "))

            if task.status == TaskStatus.COMPLETED:
                text.append(("green", "✅ "))
            else:
                if not suggested:
                    suggested = task
                    text.append(("yellow", "👉 "))
                else:
                    text.append(("", "  "))

            text.append(("italic", f" {int(task.progress * 100):>3}% - "))

            text.append(("bold", f"{task.name}"))

            choices.append(Choice(title=FormattedText(text), value=task))

        task = questionary.select(
            "Select a task:", choices=choices, default=suggested
        ).ask()

        if task is None:
            raise KeyboardInterrupt

        return task

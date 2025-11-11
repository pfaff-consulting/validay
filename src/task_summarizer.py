from rich import print
from rich.table import Table

from src.model.task import TaskStateWriteModel, SubtaskStateWriteModel, SubtaskStatus
from src.ui.loader import Loader


class SubtaskSummary:
    def __init__(self, iid: str, name: str):
        self.iid = iid
        self.name = name
        self.items = []
        self.status = None

    def add_item(self, item_name: str, status: SubtaskStatus):
        self.items.append({"name": item_name, "status": status})

    def set_status(self, status: SubtaskStatus):
        self.status = status

    def get_percent(self) -> float:
        if self.status == SubtaskStatus.COMPLETED:
            return 1

        if len(self.items) == 0:
            return 0

        return len([item for item in self.items if item["status"] == SubtaskStatus.COMPLETED]) / len(self.items)

    def to_write_model(self) -> SubtaskStateWriteModel:
        return SubtaskStateWriteModel(
            iid=self.iid,
            status=self.status,
            progress=self.get_percent()
        )


class TaskSummary:
    def __init__(self, name: str):
        self.name = name
        self.subtasks: list[SubtaskSummary] = []

    def add_subtask(self, subtask: SubtaskSummary):
        self.subtasks.append(subtask)

    def get_total_count(self):
        return len(self.subtasks)

    def get_completed_count(self):
        return len([subtask for subtask in self.subtasks if subtask.status == SubtaskStatus.COMPLETED])

    def get_todo_count(self):
        return len([subtask for subtask in self.subtasks if subtask.status == SubtaskStatus.TODO])

    def to_write_model(self) -> TaskStateWriteModel:
        return TaskStateWriteModel(
            subtaskAssessments=[s.to_write_model() for s in self.subtasks]
        )

    def get_percent(self):
        return sum([subtask.get_percent() for subtask in self.subtasks]) / len(self.subtasks)

    def display_summary(self):
        grid = Table(title="-"*40, expand=True, box=None, width=40, show_header=False)
        grid.add_column()
        grid.add_column()
        grid.add_column()

        grid.add_row("[green]Completed[/]", "[yellow]TODO[/]", "Percent")
        grid.add_row(
            f"[bold]{self.get_completed_count()}[/]",
            f"[bold]{self.get_todo_count()}[/]",
            f"[bold]{self.get_percent()*100:.0f}%[/]"
        )

        print(grid)
        print()


class TaskSummarizer:
    def __init__(self, task_name: str):
        self.spinner = Loader("Checking...")
        self.summary: dict[str, SubtaskSummary] = {}
        self.task_name = task_name
        self.task_summary = TaskSummary(task_name)

    def task_started(self, iid: str, name: str):
        print(f"[not bold italic gray50]{iid}[/] - {name}")
        self.spinner.start()
        self.summary[iid] = SubtaskSummary(iid, name)

    def task_completed(self, iid: str, status: SubtaskStatus):
        self.spinner.stop()
        self.summary[iid].set_status(status)

        self.task_summary.add_subtask(self.summary[iid])

        if status == SubtaskStatus.COMPLETED:
            print(f"    [bold green]OK[/] ([italic gray50]{self.summary[iid].get_percent() * 100:.0f}%[/])\n")
            return

        if status == SubtaskStatus.TODO:
            print(f"    [bold yellow]TODO[/] ([italic gray50]{self.summary[iid].get_percent() * 100:.0f}%[/])\n")

    def playbook_started(self):
        print(f"Evaluating task [bold italic grey50]{self.task_name}[/]\n")

    def playbook_ended(self) -> TaskSummary:
        return self.task_summary

    def item_completed(self, iid: str, item_value: str, status: SubtaskStatus):
        self.summary[iid].add_item(item_value, status)

        if status == SubtaskStatus.COMPLETED:
            print(f"    - {item_value} [green]OK[/]")
        else:
            print(f"    - {item_value} [yellow]TODO[/]")

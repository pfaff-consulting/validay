from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich import box

from src.api_manager import ApiManager
from src.config import Config
from src.exception.app_exceptions import TaskNotSelectedException, TaskNotFoundException
from src.model.task import SubtaskStatus


class TaskHintCommand:
    def __init__(self, config: Config, api: ApiManager):
        self.config = config
        self.api = api
        self.console = Console()

    def run(self) -> None:
        task_id = self.config.state.current_task
        if not task_id:
            raise TaskNotSelectedException()

        task = self.api.get_task(task_id)
        if not task:
            raise TaskNotFoundException(task_id)

        console = self.console

        target = None
        if task.subtasks:
            for st in reversed(task.subtasks):
                if st.status in {SubtaskStatus.TODO, SubtaskStatus.FAILED}:
                    target = st
                    break

        if not target:
            console.print(Panel(Text("All subtasks are completed. No hint to show.", style="green"),
                                border_style="green", box=box.SIMPLE))
            return

        # Record that a hint for this subtask was shown (for solution confirmation later)
        self.config.state.last_hint_task = task.id
        self.config.state.last_hint_subtask = target.iid

        # Header: "<orderId gray> Task name" then a line describing chosen subtask
        header = Text(justify="left")
        header.append(f"{task.orderId} ", style="grey50")
        header.append(f"{task.name}\n", style="bold")
        header.append("\n")
        # subtask line
        status_style = "yellow" if target.status == SubtaskStatus.TODO else "red"
        header.append(f"[{target.iid}] ", style="grey50")
        header.append(f"{target.name}\n")
        header.append(f"Status: ", style="grey50")
        header.append(f"{target.status.value.replace('_', ' ').title()}", style=status_style)
        header.append(f"  •  {int(target.progress * 100)}%", style="italic grey50")

        # Hint body
        hint_renderable = None
        hint_text = (target.hint or "").strip()
        if hint_text:
            try:
                hint_renderable = Markdown(hint_text)
            except Exception:
                hint_renderable = Text(hint_text)
        else:
            hint_renderable = Text("No hint provided for this subtask.", style="grey50")

        group = Group(header, Text(""), Text("HINT", style="bold cyan"), hint_renderable)
        # Compose header and hint as separate renderables to avoid assembling Markdown into Text
        # Make the panel a bit narrower for readability (within sensible bounds)
        target_width = max(60, min(120, console.width - 20))
        console.print(Panel(group, border_style="cyan", box=box.SIMPLE, width=target_width))

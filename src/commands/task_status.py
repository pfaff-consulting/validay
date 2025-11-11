from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich import box

from src.api_manager import ApiManager
from src.config import Config
from src.exception.app_exceptions import TaskNotSelectedException, TaskNotFoundException
from src.model.task import TaskStatus, SubtaskStatus


class TaskStatusCommand:
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

        # Header: "<orderId gray> Task name" on first line, blank line, state+progress, then italic ID line
        status_map = {
            TaskStatus.COMPLETED: ("✅  Completed", "green"),
            TaskStatus.STARTED: ("⏳  In progress", "yellow"),
            TaskStatus.NOT_STARTED: ("🕘  Not started", "grey50"),
            TaskStatus.FAILED: ("❌  Failed", "red"),
        }
        status_text, status_color = status_map.get(task.status, (str(task.status), "white"))

        header = Text(justify="left")
        header.append(f"{task.orderId} ", style="grey50")
        header.append(f"{task.name}", style="bold")

        header.append(f"\n" + " "*len(task.orderId) + " ")
        header.append(f"ID: ", style="grey50")
        header.append(f"{task.id}\n\n", style="italic grey50")
        header.append(status_text, style=status_color)
        header.append(f"  •  {int(task.progress * 100)}%", style="italic grey50")

        # Description — short preview (first paragraph), Markdown if possible
        desc_renderable = None
        if task.description:
            short_desc = task.description.strip().split("\n\n")[0].strip()
            try:
                desc_renderable = Markdown(short_desc)
            except Exception:
                desc_renderable = Text(short_desc)

        # Subtasks — compact table (no expand to avoid long spacing); also show aggregate % done
        completed = 0
        total = 0
        if task.subtasks:
            total = len(task.subtasks)
            completed = len([st for st in task.subtasks if st.status == SubtaskStatus.COMPLETED])
        pct_done = int((completed / total) * 100) if total else 0
        subtasks_header = Text(f"Subtasks — {pct_done}%", style="bold")
        if total:
            subtasks_header.append(f"  (", style="")
            subtasks_header.append(f"{completed}", style="green")
            subtasks_header.append(f"/{total})", style="")

        table = Table(
            show_header=True,
            header_style="bold",
            show_lines=False,
            expand=False,
            box=box.SIMPLE,
            padding=(0, 1),
        )
        table.add_column("IID", justify="right", style="grey50", no_wrap=True)
        table.add_column("Subtask", overflow="fold")
        table.add_column("Status", justify="right", no_wrap=True)

        if task.subtasks:
            for st in task.subtasks:
                if st.status == SubtaskStatus.COMPLETED:
                    stt = f"[green]OK[/]"
                elif st.status == SubtaskStatus.FAILED:
                    stt = f"[red]FAILED[/]"
                else:
                    stt = f"([grey50]{int(st.progress * 100)}%[/]) [yellow]TODO[/]"

                table.add_row(st.iid, st.name, stt)
        else:
            table.add_row("-", "No subtasks available", "-")

        # Group all into a single Panel to keep everything in one place
        content_parts = [header]
        if desc_renderable:
            content_parts.append(Text(""))  # spacing line
            content_parts.append(desc_renderable)
        content_parts.append(Text(""))
        content_parts.append(subtasks_header)
        content_parts.append(table)

        group = Group(*content_parts)
        console.print(Panel(group, border_style="cyan", box=box.SIMPLE))

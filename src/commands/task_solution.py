from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich import box

from questionary import confirm

from src.api_manager import ApiManager
from src.config import Config
from src.exception.app_exceptions import TaskNotSelectedException, TaskNotFoundException
from src.model.task import SubtaskStatus


class TaskSolutionCommand:
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
            console.print(Panel(Text("All subtasks are completed. Nothing to solve.", style="green"),
                                border_style="green", box=box.SIMPLE))
            return

        # Confirm if the hint for this exact subtask wasn't viewed
        last_hint_task = self.config.state.last_hint_task
        last_hint_subtask = self.config.state.last_hint_subtask
        if not (last_hint_task == task.id and last_hint_subtask == target.iid):
            proceed = confirm(
                "You haven't viewed the hint for this subtask. Reveal the solution anyway?",
                default=False,
            ).ask()
            if not proceed:
                console.print(Panel(Text("Aborted showing solution.", style="yellow"), border_style="yellow", box=box.SIMPLE))
                return

        # Header
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

        # Solution body (render as a CODE block)
        solution_text = (target.solution or "").strip()

        def _syntax_from_text(text: str):
            if not text:
                return Text("No solution provided for this subtask.", style="grey50")

            # Find first fenced code block anywhere in the text: ```lang\n...\n```
            import re

            def _alias(lang: str) -> str:
                if not lang:
                    return "text"
                l = lang.lower().strip()
                aliases = {
                    "sh": "bash",
                    "shell": "bash",
                    "zsh": "bash",
                    "ps": "powershell",
                    "pwsh": "powershell",
                    "ps1": "powershell",
                    "yml": "yaml",
                    "tf": "terraform",
                    "hcl": "terraform",
                    "js": "javascript",
                    "ts": "typescript",
                    "md": "markdown",
                    "txt": "text",
                    "py": "python",
                    "rb": "ruby",
                    "rs": "rust",
                    "c++": "cpp",
                    "c#": "csharp",
                    "kt": "kotlin",
                    "golang": "go",
                }
                return aliases.get(l, l or "text")

            fence_re = re.compile(r"```\s*([a-zA-Z0-9_+#-]*)\s*\n(.*?)\n```", re.DOTALL)
            m = fence_re.search(text)
            if m:
                lang = _alias(m.group(1))
                code = m.group(2)
            else:
                # No fenced block – use whole text as code and guess language heuristically
                lines = [ln for ln in text.splitlines() if ln.strip() != ""]
                lang = "text"
                if lines:
                    first = lines[0].strip()
                    # Shebang detection
                    if first.startswith("#!/") or first.startswith("#!/usr/bin/env"):
                        if "python" in first:
                            lang = "python"
                        elif "bash" in first or "sh" in first:
                            lang = "bash"
                        elif "pwsh" in first or "powershell" in first:
                            lang = "powershell"
                        elif "node" in first:
                            lang = "javascript"
                    else:
                        sample = "\n".join(lines[:10])
                        # Very light heuristics
                        if re.search(r"^\s*version\s*:\s*\d+", sample, re.I | re.M) and ":" in sample:
                            lang = "yaml"
                        elif re.search(r"^\s*\{.*\}\s*$", sample.strip(), re.S):
                            lang = "json"
                        elif re.search(r"^\s*FROM\s+\S+", sample, re.I | re.M):
                            lang = "dockerfile"
                        elif re.search(r"^\s*import\s+\w+|def\s+\w+\(", sample):
                            lang = "python"
                        elif re.search(r"^\s*function\s+\w+|console\.log\(", sample):
                            lang = "javascript"
                code = text

            # Trim trailing blank lines for nicer rendering
            code = re.sub(r"\n+\Z", "\n", code)

            try:
                return Syntax(code, lang or "text", word_wrap=False, line_numbers=False)
            except Exception:
                return Syntax(code, "text", word_wrap=False, line_numbers=False)

        solution_renderable = _syntax_from_text(solution_text)

        group = Group(header, Text(""), Text("SOLUTION", style="bold magenta"), solution_renderable)
        target_width = max(60, min(120, console.width - 20))
        console.print(Panel(group, border_style="magenta", box=box.SIMPLE, width=target_width))

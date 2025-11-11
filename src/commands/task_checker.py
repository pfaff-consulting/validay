from src.task_runner import TaskRunner
from src.api_manager import ApiManager
from src.config import Config
from src.exception.app_exceptions import TaskNotSelectedException, TaskNotFoundException
from src.ui.loader import Loader


class TaskChecker:
    def __init__(self, config: Config, api: ApiManager):
        self.api = api
        self.config = config

    def run(self) -> None:
        task_id = self.config.state.current_task

        if not task_id:
            raise TaskNotSelectedException()

        task = self.api.get_task(task_id)

        if not task:
            raise TaskNotFoundException(task_id)

        runner = TaskRunner(task_name=task.name, code=task.code)
        result = runner.run()

        spinner = Loader("Calculating task result...", padding=0)
        spinner.start()
        self.api.report_task_assessment(task_id, result.to_write_model())
        spinner.stop()

        result.display_summary()

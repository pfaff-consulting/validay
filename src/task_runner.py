import os
import tempfile
import re

from io import StringIO
from typing import Tuple

import ansible_runner
from ruamel.yaml import YAML

from src.task_summarizer import TaskSummarizer, SubtaskStatus, TaskSummary


class TaskRunner:
    def __init__(self, task_name, code: str):
        self.code = self.__prepare_playbook_code(code)
        self.summarizer = TaskSummarizer(task_name)
        pass

    def run(self) -> TaskSummary:
        private_data_dir, playbook_path = self.__create_ansible_data_dir(self.code)

        self.summarizer.playbook_started()
        ansible_runner.run(
            private_data_dir=private_data_dir,
            playbook=playbook_path,
            inventory="localhost,",
            cmdline="--check",
            event_handler=self.handle_event,
            quiet=True,
        )
        return self.summarizer.playbook_ended()

    def handle_event(self, event_data):
        event = event_data.get('event')
        data = event_data.get('event_data', {})

        if event.startswith("runner_on") or event.startswith("playbook_on") or event.startswith("runner_item_on"):
            task_name = data.get('task', 'UNKNOWN TASK')

            if task_name == "UNKNOWN TASK":
                return

            match = re.match(r"\[(\d+)]\s*(.*)", task_name)
            if match:
                iid = match.group(1)
                task_name = match.group(2)
            else:
                return

            if event == 'playbook_on_task_start':
                self.summarizer.task_started(iid, task_name)

            elif event == "runner_on_ok":
                changed = data.get('res', {}).get('changed', 'UNKNOWN STATUS')

                if changed == 'UNKNOWN STATUS':
                    raise Exception

                self.summarizer.task_completed(iid, SubtaskStatus.TODO if changed else SubtaskStatus.COMPLETED)

            elif event == "runner_on_failed":
                self.summarizer.task_completed(iid, SubtaskStatus.TODO)

            elif event == "runner_item_on_ok":
                # extract item value from common locations
                item_val = data.get('item')
                if item_val is None:
                    item_val = data.get('res', {}).get('item')
                if item_val is None:
                    item_val = "<item>"

                changed = data.get('res', {}).get('changed', 'UNKNOWN STATUS')

                if changed == 'UNKNOWN STATUS':
                    raise Exception

                self.summarizer.item_completed(iid, str(item_val), SubtaskStatus.TODO if changed else SubtaskStatus.COMPLETED)

            elif event == "runner_item_on_failed":
                item_val = data.get('item')
                if item_val is None:
                    item_val = data.get('res', {}).get('item')
                if item_val is None:
                    item_val = "<item>"
                self.summarizer.item_completed(iid, str(item_val), SubtaskStatus.TODO)

    def __prepare_playbook_code(self, code: str) -> str:
        yaml = YAML()
        yaml.preserve_quotes = True
        data = yaml.load(code)

        for play in data:
            play["hosts"] = "localhost"

        buf = StringIO()
        yaml.dump(data, buf)
        return buf.getvalue()

    def __create_ansible_data_dir(self, code: str) -> Tuple[str, str]:
        runner_data_dir = tempfile.mkdtemp()
        project_dir = os.path.join(runner_data_dir, 'project')
        playbook_path = os.path.join(project_dir, 'playbook.yaml')

        os.makedirs(project_dir)
        with open(playbook_path, "w") as f:
            f.write(code)
            f.flush()

        return runner_data_dir, playbook_path

import os
import yaml
from rich import print


class ConfigState:
    def __init__(self, config_path: str, data: dict):
        self._config_path = config_path
        self._data = data or {}

    @property
    def current_course(self):
        return self._data.get("current_course")

    @current_course.setter
    def current_course(self, value):
        self._data["current_course"] = value
        self.__flush()

    @property
    def current_task(self):
        return self._data.get("current_task")

    @current_task.setter
    def current_task(self, value):
        self._data["current_task"] = value
        self.__flush()

    @property
    def last_hint_task(self):
        return self._data.get("last_hint_task")

    @last_hint_task.setter
    def last_hint_task(self, value):
        self._data["last_hint_task"] = value
        self.__flush()

    @property
    def last_hint_subtask(self):
        return self._data.get("last_hint_subtask")

    @last_hint_subtask.setter
    def last_hint_subtask(self, value):
        self._data["last_hint_subtask"] = value
        self.__flush()

    def __flush(self):
        """Write changes to YAML file."""
        try:
            with open(self._config_path, "r") as f:
                config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            config = {}

        config.setdefault("state", {})
        config["state"].update(self._data)

        with open(self._config_path, "w") as f:
            yaml.safe_dump(config, f, sort_keys=False)


class Config:
    def __init__(self, config_path: str, base_url: str, api_token: str, state: dict):
        self._config_path = config_path
        self.base_url = base_url
        self.api_token = api_token
        self.state = ConfigState(config_path, state)

    @staticmethod
    def from_file(file_path: str):
        if not os.path.exists(file_path):
            print(
                f"[red]Config file not found where expected ([italic]{file_path}[/italic])."
            )
            exit(1)

        with open(file_path, "r") as f:
            try:
                config = yaml.safe_load(f) or {}
                api = config["api"]
                state = config["state"]

                return Config(
                    config_path=file_path,
                    base_url=api["base_url"],
                    api_token=api["auth_token"],
                    state=state,
                )
            except yaml.YAMLError as e:
                print(
                    f"[red]Error while parsing config file ([italic]{file_path}[/italic])."
                )
                print(e)
                exit(1)

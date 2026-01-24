import requests

from src.model.task import TaskStateReadModel, TaskStateWriteModel


class ApiManager:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.strip('/')
        self.api_token = api_token

    def get_task_list(self, course_id: int) -> list[TaskStateReadModel]:
        data = self.__get_api_call(
            f"/api/tasks/task-states?courseId={course_id}"
        ).json()
        return [TaskStateReadModel.model_validate(item) for item in data]

    def get_task(self, task_id: str) -> TaskStateReadModel | None:
        resp = self.__get_api_call(f"/api/tasks/task-states/{task_id}/details")

        if resp.status_code == 404:
            return None

        if resp.status_code != 200:
            raise Exception

        return TaskStateReadModel.model_validate(resp.json())

    def report_task_assessment(self, task_id: str, task_state: TaskStateWriteModel) -> None:
        resp = self.__post_api_call(f"/api/tasks/task-states/{task_id}/report", task_state.model_dump())

        if resp.status_code != 200:
            raise Exception

    def __post_api_call(self, uri: str, payload: dict):
        return requests.post(
            self.base_url + uri,
            headers={
                "X-Personal-Access-Token": self.api_token,
            },
            json=payload
        )

    def __get_api_call(self, uri: str):
        return requests.get(
            self.base_url + uri,
            headers={
                "X-Personal-Access-Token": self.api_token,
            },
        )

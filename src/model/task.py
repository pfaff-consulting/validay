from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class TaskStatus(str, Enum):
    COMPLETED = "completed"
    STARTED = "started"
    NOT_STARTED = "not_started"
    FAILED = "failed"


class SubtaskStatus(str, Enum):
    COMPLETED = "completed"
    TODO = "todo"
    FAILED = "failed"


class SubtaskStateReadModel(BaseModel):
    iid: str
    name: str
    hint: str
    solution: str
    status: SubtaskStatus
    progress: float


class TaskStateReadModel(BaseModel):
    id: str

    orderId: str
    name: str
    description: str

    attempts: int
    progress: float

    status: TaskStatus

    code: Optional[str] = None
    subtasks: Optional[List[SubtaskStateReadModel]] = None


class SubtaskStateWriteModel(BaseModel):
    iid: str
    status: SubtaskStatus
    progress: float


class TaskStateWriteModel(BaseModel):
    subtaskAssessments: List[SubtaskStateWriteModel]

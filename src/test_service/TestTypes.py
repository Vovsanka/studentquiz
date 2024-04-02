from datetime import datetime

from typing import Any
from pydantic import BaseModel

from test_service.TaskTypes import Task


class TestInfo(BaseModel):
    id: str
    name: str
    description: str


class Test(BaseModel):
    info: TestInfo
    tasks: list[Task]
    pass_percents: float





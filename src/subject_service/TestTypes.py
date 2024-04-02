from datetime import datetime

from typing import Any
from pydantic import BaseModel

from subject_service.TaskTypes import Task


class TestInfo(BaseModel):
    id: str
    name: str
    description: str


class Test(BaseModel):
    info: TestInfo
    tasks: list[Task]
    pass_percents: float


class TestSolutionAttempt(BaseModel):
    solved_by: str
    solved_at: datetime
    answers: list[Any]

class CheckedAttempt(BaseModel):
    solution_attempt: TestSolutionAttempt
    task_points: list[float]
    attempt_points: float
    overall_points: int
    attempt_percents: float
    passed: bool

class TestInstance(BaseModel):
    test: Test
    remark: str
    published_at: datetime
    published_by: str
    solution_attempts: list[CheckedAttempt]

class TestSummary(BaseModel):
    passed: int
    attempts_count: int
    average: float



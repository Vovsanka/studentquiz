from enum import Enum

from pydantic import BaseModel
from typing import Any


class TaskType(str, Enum):
    SINGLE_CHOICE = 'single-choice',
    MULTIPLE_CHOICE = 'multiple-choice'


class Task(BaseModel):
    question: str
    tag: str
    options: list
    type: TaskType
    answer: Any
    points: int
    
    def check_answer(self, answer: Any) -> float:
        raise Exception('Specified only for the derived classes!')


class SingleChoiceTask(Task):
    options: list[str]
    answer: int

    # method override
    def check_answer(self, answer : int) -> float:
        if self.answer == answer:
            return self.points
        return 0


class MultipleChoiceTask(Task):
    options: list[str]
    answer: set[int]

    # method override
    def check_answer(self, answer : set[int]) -> float:
        if len(self.options) == 0:
            return self.points
        wrong_answers =  len(self.answer.symmetric_difference(set(answer)))
        correct_answers = len(self.options) - wrong_answers
        return (correct_answers / len(self.options)) * self.points

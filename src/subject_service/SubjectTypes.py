from pydantic import BaseModel

from subject_service.TestTypes import TestInstance



class SubjectInfo(BaseModel):
    id: str
    name: str
    description: str
    owner: str  # username
    teachers: list[str]  # only teacher usernames!


class Subject(BaseModel):
    info: SubjectInfo
    student_access_code: str
    teacher_access_code: str
    students: list[str]  # only student usernames!
    test_instances: list[TestInstance]

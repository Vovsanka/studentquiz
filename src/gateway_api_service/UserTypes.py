from enum import Enum

from pydantic import BaseModel


class Credentials(BaseModel):
    username: str
    password: str

class Role(str, Enum):
    ADMIN = 'admin',
    TEACHER = 'teacher'
    STUDENT = 'student'

class UserInfo(BaseModel):
    username: str
    name: str
    role: Role
    token: str

class User(BaseModel):
    info: UserInfo
    credentials: Credentials




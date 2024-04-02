export interface User {
  info: UserInfo
  credentials: Credentials
}

export interface UserInfo {
  username: string
  name: string
  role: Role
  token: string
}

export interface Credentials {
  username: string
  password: string
}

export enum Role {
  NONE = 'none',
  ADMIN = 'admin',
  TEACHER = 'teacher',
  STUDENT = 'student'
}

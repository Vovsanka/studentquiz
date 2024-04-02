import type { TestInstance, Test } from "./TestTypes"

export interface SubjectInfo {
    id: string
    name: string
    description: string
    owner: string,
    teachers: Array<string>,
    
}

export interface Subject {
    info: SubjectInfo
    student_access_code: string
    teacher_access_code: string
    students: Array<string>
    test_instances: Array<TestInstance>
}
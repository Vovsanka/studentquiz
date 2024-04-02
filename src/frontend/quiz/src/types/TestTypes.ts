export enum TaskType {
    SINGLE_CHOICE = 'single-choice',
    MULTIPLE_CHOICE = 'multiple-choice'
}

export interface Task {
    question: string
    tag: string
    options: Array<any>
    type: TaskType
    points: number
    answer: any
}

export interface SingleChoice extends Task {
    options: Array<string>
    answer: number
}

export interface MultipleChoice extends Task {
    options: Array<string>
    answer: Array<number>
}


export interface TestInfo {
    id: string
    name: string
    description: string
}

export interface Test {
    info: TestInfo
    tasks: Array<Task>
    pass_percents: number
}

export interface TestSolutionAttempt {
    solved_by: string
    solved_at: Date
    answers: Array<Object>
}

export interface CheckedAttempt {
    solution_attempt: TestSolutionAttempt
    task_points: Array<number>
    attempt_points: number
    overall_points: number
    attempt_percents: number
    passed: boolean
}

export interface TestInstance {
    test: Test
    remark: string
    published_at: string
    published_by: string
    solution_attempts: Array<CheckedAttempt>
}

export interface TestSummary {
    passed: number
    attempts_count: number
    average: number
}
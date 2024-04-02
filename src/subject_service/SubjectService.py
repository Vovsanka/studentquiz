import json
from datetime import datetime, timezone
from typing import Optional
import random
import string

import requests as req

from flask_cors import CORS
from flask import Flask, Response, request

from subject_service.TaskTypes import TaskType, SingleChoiceTask, MultipleChoiceTask
# from global_types.UserTypes import UserInfo, Role
from subject_service.TestTypes import Test, TestInfo, TestInstance, TestSolutionAttempt, CheckedAttempt, TestSummary
from subject_service.SubjectTypes import SubjectInfo, Subject



class SubjectService:

    def __init__(self, app : Flask, service_api_url : str):
        self.app = app
        self.service_api_url = service_api_url
        # restrictions
        self.cors = CORS(self.app)
        # endpoints
        self._register_routes()
        # init database
        self._init_database()
        # admins list
        self.admins = ['admin']
        # init successfull
        self.app.logger.info("SubjectService inited!")

    def _register_routes(self):
        self.app.route('/subject_service/get_my_subjects_info', methods=['GET'])(self._get_my_subjects_info)
        self.app.route('/subject_service/get_all_subjects_info', methods=['GET'])(self._get_all_subjects_info)
        self.app.route('/subject_service/get_subject_info/<subject_id>', methods=['GET'])(self._get_subject_info)
        self.app.route('/subject_service/get_subjects_info_published/<test_id>', methods=['GET'])(self._get_subjects_info_published)

        self.app.route('/subject_service/get_subject', methods=['GET', 'POST'])(self._create_empty_subject)
        self.app.route('/subject_service/get_subject/<subject_id>', methods=['GET'])(self._get_subject)
        self.app.route('/subject_service/save_subject/<subject_id>', methods=['PUT'])(self._save_subject)
        self.app.route('/subject_service/delete_subject/<subject_id>', methods=['DELETE'])(self._delete_subject)

        self.app.route('/subject_service/publish_test/<subject_id>/<test_id>', methods=['POST'])(self._publish_test)
        self.app.route('/subject_service/delete_test_instance/<subject_id>', methods=['DELETE'])(self._delete_test_instance)

        self.app.route('/subject_service/subject_subscribe_student/<subject_id>', methods=["POST"])(self._subject_subscribe_student)
        self.app.route('/subject_service/subject_subscribe_teacher/<subject_id>', methods=["POST"])(self._subject_subscribe_teacher)
        self.app.route('/subject_service/remove_teacher_from_subject/<subject_id>/<username>', methods=["DELETE"])(self._remove_teacher)
        self.app.route('/subject_service/remove_student_from_subject/<subject_id>/<username>', methods=["DELETE"])(self._remove_student)

        self.app.route('/subject_service/save_test_attempt/<subject_id>', methods=["POST"])(self._save_test_attempt)
        self.app.route('/subject_service/get_task_results/<subject_id>', methods=['GET'])(self._get_task_results)
        self.app.route('/subject_service/get_test_summary/<subject_id>', methods=['GET'])(self._get_test_summary)
        self.app.route('/subject_service/get_student_results/<subject_id>', methods=['GET'])(self._get_student_results)

        self.app.before_request(self._before_request)

    def _before_request(self):
        # check service secret
        if request.headers.get('ServiceSecret') != self.app.config["SERVICE_SECRET"]:
            return Response(status=500, response=json.dumps(["Cannot access SubjectService", "only GatewayAPI may access SubjectService"]))

    def _init_database(self):
        # Data-structures that simulate a service database
        self.SUBJECTS_DATABASE = dict()
        self.ID_DATABASE = dict()
        # fill database with some entities for testing
        self._prefill_database() 

    ### helper methods
    def _generate_subject_id(self, username):
        if username not in self.ID_DATABASE:
            self.ID_DATABASE[username] = 0
        new_id = self.ID_DATABASE[username] = self.ID_DATABASE[username] + 1
        return f'{username}_subject_{new_id}'
    
    def _check_subject_teacher(self, username : str, subject_id : str) -> None:
        if subject_id not in self.SUBJECTS_DATABASE:
                raise Exception("no such subject")     
        if username not in self.SUBJECTS_DATABASE[subject_id].info.teachers:
            raise Exception('To perform this operation you have to be a subject teacher or owner')
        
    def _check_subject_student(self, username : str, subject_id : str) -> None:
        if subject_id not in self.SUBJECTS_DATABASE:
                raise Exception("no such subject")     
        if username not in self.SUBJECTS_DATABASE[subject_id].students:
            raise Exception('To perform this operation you have to be a subject student')
        
    def _check_subject_participant(self, username : str, subject_id : str) -> None:
        if subject_id not in self.SUBJECTS_DATABASE:
                raise Exception("no such subject")     
        if username not in self.SUBJECTS_DATABASE[subject_id].info.teachers and username not in self.SUBJECTS_DATABASE[subject_id].students:
            raise Exception('To perform this operation you have to be a subject teacher or student')
    
    def _cut_for_student(self, student : string, subject : Subject) -> Subject:
        student_subject = Subject(
            info=subject.info,
            teacher_access_code='',
            student_access_code='',
            students=[],
            test_instances=[]
        )
        for original_instance in subject.test_instances:
            student_attempts = []
            for original_attempt in original_instance.solution_attempts:
                if original_attempt.solution_attempt.solved_by == student:
                    student_attempts.append(original_attempt)
            student_subject.test_instances.append(TestInstance(
                test=self._cut_test_answers(original_instance.test),
                remark=original_instance.remark,
                published_at=original_instance.published_at,
                published_by=original_instance.published_by,
                solution_attempts=student_attempts
            ))
        return student_subject
    
    def _cut_test_answers(self, test : Test) -> Test:
        new_tasks = []
        for task in test.tasks:
            if task.type == TaskType.SINGLE_CHOICE:
                new_tasks.append(SingleChoiceTask(
                    question=task.question,
                    tag=task.tag,
                    options=task.options,
                    type=task.type,
                    answer=-1,
                    points=task.points
                ))
            if task.type == TaskType.MULTIPLE_CHOICE:
                new_tasks.append(MultipleChoiceTask(
                    question=task.question,
                    tag=task.tag,
                    options=task.options,
                    type=task.type,
                    answer=[],
                    points=task.points
                ))
        return Test(
            info=test.info,
            tasks=new_tasks,
            pass_percents=test.pass_percents
        )
    
    def _specify_test_tasks(self, test : Test) -> Test:
        return Test(
            info=test.info,
            tasks=[SingleChoiceTask(
                question=task.question,
                tag=task.tag,
                options=task.options,
                type=task.type,
                answer=task.answer,
                points=task.points
            ) if task.type == TaskType.SINGLE_CHOICE
              else MultipleChoiceTask(
                question=task.question,
                tag=task.tag,
                options=task.options,
                type=task.type,
                answer=task.answer,
                points=task.points
              ) for task in test.tasks ],
            pass_percents=test.pass_percents
        )

            
    def _generate_string(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def _check_attempt(self, solution_attempt : TestSolutionAttempt, test : Test):
        test = self._specify_test_tasks(test)
        self.app.logger.debug(solution_attempt.answers)
        task_points = []
        self.app.logger.debug(test.tasks)
        for index, answer in enumerate(solution_attempt.answers):
            task_points.append(test.tasks[index].check_answer(answer))
        self.app.logger.debug(task_points)
        attempt_points = sum(task_points)
        overall_points = sum([task.points for task in test.tasks])
        try:
            attempt_percents = attempt_points / overall_points * 100
        except Exception:
            attempt_percents = 100
        passed = (attempt_percents >= test.pass_percents)
        return CheckedAttempt(
            solution_attempt=solution_attempt,
            task_points=task_points,
            attempt_points=attempt_points,
            overall_points=overall_points,
            attempt_percents=attempt_percents,
            passed=passed
        )

    ### Subject service endpoints

    def _get_subjects_info_published(self, test_id: str):
        try:
            username = request.args['username']
            result_subjects= []
            for subject in self.SUBJECTS_DATABASE.values():
                test_is_published = test_id in [test_instance.test.info.id for test_instance in subject.test_instances]
                if test_is_published and (username in subject.info.teachers):
                    result_subjects.append(subject.info)
            return Response(response=json.dumps([subject_info.model_dump_json() for subject_info in result_subjects]))
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve the subjects the test is published on", str(e)]))
    
    def _get_my_subjects_info(self):
        username = request.args['username']
        try:                
            result_subjects= []
            for subject in self.SUBJECTS_DATABASE.values():
                if username in subject.info.teachers or username in subject.students:
                    result_subjects.append(subject.info)
            return Response(response=json.dumps([subject_info.model_dump_json() for subject_info in result_subjects]))
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve my subjects info", str(e)]))
        
    def _get_all_subjects_info(self):
        try:  
            return Response(response=json.dumps([subject.info.model_dump_json() for subject in self.SUBJECTS_DATABASE.values()]))
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve all subjects info", str(e)]))
        
    def _get_subject_info(self, subject_id: str):
        try:
            if subject_id not in self.SUBJECTS_DATABASE:
                raise Exception("no such subject")                
            subject = self.SUBJECTS_DATABASE[subject_id]
            return Response(response=subject.info.model_dump_json())
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve the subject info", str(e)]))
    
    def _publish_test(self, subject_id : str, test_id : str):
        try:
            username = request.args['username']
            self._check_subject_teacher(username, subject_id)
            remark = json.loads(request.form['remark'])
            #
            test_response = req.get(f'{self.service_api_url}/service_api/get_test/{test_id}',
                                    headers = {'username': username, 'ServiceSecret': self.app.config['SERVICE_API_SECRET']},
                                    verify=False)
            if test_response.status_code != 200:
                raise Exception('cannot retrieve the publisher info')
            test = Test.model_validate_json(test_response.text)
            #
            for test_instance in self.SUBJECTS_DATABASE[subject_id].test_instances:
                if test_instance.test.info.id == test_id and test_instance.remark == remark:
                    raise Exception('test instance with this test_id and remark already exists.')
            #
            if subject_id not in self.SUBJECTS_DATABASE:
                raise Exception("no such subject")     
            self.SUBJECTS_DATABASE[subject_id].test_instances.append(TestInstance(
                test=test,
                remark=remark,
                published_at=datetime.utcnow().replace(tzinfo=timezone.utc),
                published_by=username,
                solution_attempts=[]
            ))
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot publish test on this subject", str(e)]))
    
    def _create_empty_subject(self):
        try:
            username = request.args['username']
            empty_subject = Subject(
                info=SubjectInfo(
                    id=self._generate_subject_id(username),
                    name="",
                    description="",
                    owner = username,
                    teachers = [username],
                ),
                test_instances=[],
                teacher_access_code=self._generate_string(),
                student_access_code=self._generate_string(),
                students = [],  
            )
            # save the empty subject
            self.SUBJECTS_DATABASE[empty_subject.info.id] = empty_subject
            return Response(response=empty_subject.model_dump_json())
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot create an empty subject", str(e)]))
        
    def _save_subject(self, subject_id : str):
        try:
            username = request.args['username']
            self._check_subject_teacher(username, subject_id)
            subject = Subject.model_validate_json(request.form['subject'])
            # save the empty subject
            if subject_id not in self.SUBJECTS_DATABASE:
                raise Exception("no such subject")     
            self.SUBJECTS_DATABASE[subject_id] = subject
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot save the subject", str(e)]))
        
    def _delete_subject(self, subject_id : str):
        try:
            username = request.args['username']
            if username not in self.admins:
                self._check_subject_teacher(username, subject_id)
            if subject_id not in self.SUBJECTS_DATABASE:
                raise Exception("no such subject")     
            del self.SUBJECTS_DATABASE[subject_id]
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot delete the subject", str(e)]))

    def _get_subject(self, subject_id : Optional[str] = None):
        try:
            username = request.args['username']
            if username not in self.admins:
                self._check_subject_participant(username, subject_id)

            if subject_id not in self.SUBJECTS_DATABASE:
                raise Exception("no such subject")     
            subject = Subject.model_validate(self.SUBJECTS_DATABASE[subject_id])
    
            if username not in subject.info.teachers:
                return Response(response=self._cut_for_student(username, subject).model_dump_json())

            return Response(response=subject.model_dump_json())
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve the subject", str(e)]))
        
    def _delete_test_instance(self, subject_id : str):
        try:
            username = request.args['username']
            if subject_id not in self.SUBJECTS_DATABASE:
                raise Exception("no such subject")     
            if username not in self.admins:
                self._check_subject_teacher(username, subject_id)
            test_id = request.args['test_id']
            remark = request.args['remark']

            delete_instance = None
            for test_instance in self.SUBJECTS_DATABASE[subject_id].test_instances:
                if test_instance.test.info.id == test_id and test_instance.remark == remark:
                    delete_instance = test_instance
                    break
            if delete_instance is None:
                raise Exception('no such test instance in the subject')
            self.SUBJECTS_DATABASE[subject_id].test_instances.remove(delete_instance)
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot delete the test instance", str(e)]))
    
    def _subject_subscribe_teacher(self, subject_id : str):
        try:
            username = request.args['username']
            access_code = json.loads(request.form['access_code'])
            if self.SUBJECTS_DATABASE[subject_id].teacher_access_code == access_code:
                if username not in self.SUBJECTS_DATABASE[subject_id].info.teachers:
                    self.SUBJECTS_DATABASE[subject_id].info.teachers.append(username)
                else:
                    raise Exception('you are already a teacher in the subject')
            else:
                raise Exception("wrong teacher access code")
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot add teacher to the subject", str(e)]))
        
    def _subject_subscribe_student(self, subject_id : str):
        try:
            username = request.args['username']
            access_code = json.loads(request.form['access_code'])
            if self.SUBJECTS_DATABASE[subject_id].student_access_code == access_code:
                if username not in self.SUBJECTS_DATABASE[subject_id].students:
                    self.SUBJECTS_DATABASE[subject_id].students.append(username)
                else:
                    raise Exception('you are already a student in the subject')
            else:
                raise Exception("wrong student access code")
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot add student", str(e)]))
        
    def _remove_teacher(self, subject_id : str, username : str):
        try:
            modifier_username = request.args['username']
            self._check_subject_teacher(modifier_username, subject_id)
            if username not in self.SUBJECTS_DATABASE[subject_id].info.teachers:
                raise Exception('no such teacher in the subject')
            if username == self.SUBJECTS_DATABASE[subject_id].info.owner:
                raise Exception('you can not remove the subject owner.')
            self.SUBJECTS_DATABASE[subject_id].info.teachers.remove(username)
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot remove teacher", str(e)]))
        
    def _remove_student(self, subject_id : str, username : str):
        try:
            modifier_username = request.args['username']
            self._check_subject_teacher(modifier_username, subject_id)
            if username not in self.SUBJECTS_DATABASE[subject_id].students:
                raise Exception('no such student in the subject')
            self.SUBJECTS_DATABASE[subject_id].students.remove(username)
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot remove student", str(e)]))

    def _save_test_attempt(self, subject_id : str):
        try:
            solver = request.args['username']
            self._check_subject_student(solver, subject_id)
            test_id = json.loads(request.form['test_id'])
            remark = json.loads(request.form['remark'])
            answers = json.loads(request.form['answers'])
            solution_attempt = TestSolutionAttempt(
                solved_by=solver,
                solved_at=datetime.utcnow().replace(tzinfo=timezone.utc),
                answers=answers
            )
            for test_instance in self.SUBJECTS_DATABASE[subject_id].test_instances:
                if test_instance.test.info.id == test_id and test_instance.remark == remark:
                    for attempt in test_instance.solution_attempts:
                        if attempt.solution_attempt.solved_by == solver:
                            raise Exception('this student has already submitted the test')
                    checked_attempt = self._check_attempt(solution_attempt, test_instance.test)
                    test_instance.solution_attempts.append(checked_attempt)
                    self.app.logger.debug(test_instance.solution_attempts)
                    return Response(status=200, response=checked_attempt.model_dump_json())
            raise Exception('no such test instance in the subject')
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot save the test attempt", str(e)]))
        
    def _get_task_results(self, subject_id : str):
        try:
            username = request.args['username']
            self._check_subject_teacher(username, subject_id)
            test_id = request.args['test_id']
            remark = request.args['remark']
            for test_instance in self.SUBJECTS_DATABASE[subject_id].test_instances:
                if test_instance.test.info.id == test_id and test_instance.remark == remark:
                    # picked answers for each task
                    picked = [[] for _ in range(len(test_instance.test.tasks))]
                    for attempt in test_instance.solution_attempts:
                        for index, answer in enumerate(attempt.solution_attempt.answers):
                            picked[index].append(answer)
                    # task results
                    attempts_amount = len(test_instance.solution_attempts)
                    task_results = []
                    for task_index, task in enumerate(test_instance.test.tasks):
                        task_results.append([])
                        if task.type == TaskType.SINGLE_CHOICE:
                            for option_index in range(len(task.options)):
                                if attempts_amount > 0:
                                    task_results[-1].append(picked[task_index].count(option_index) / attempts_amount * 100)
                                else:
                                    task_results[-1].append(0)
                        elif task.type == TaskType.MULTIPLE_CHOICE:
                            multiple_picked_options = []
                            for multiple_answer in picked[task_index]:
                                multiple_picked_options += multiple_answer
                            for option_index in range(len(task.options)):
                                if attempts_amount > 0:
                                    task_results[-1].append(multiple_picked_options.count(option_index) / attempts_amount * 100)
                                else:
                                    task_results[-1].append(0)
                    return Response(status=200, response=json.dumps(task_results))
            raise Exception('no such test instance in the subject')
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot get the task results", str(e)]))
        
    def _get_test_summary(self, subject_id : str):
        try:
            username = request.args['username']
            self._check_subject_teacher(username, subject_id)
            test_id = request.args['test_id']
            remark = request.args['remark']
            for test_instance in self.SUBJECTS_DATABASE[subject_id].test_instances:
                if test_instance.test.info.id == test_id and test_instance.remark == remark:
                    try:
                        average_score = sum([attempt.attempt_percents for attempt in test_instance.solution_attempts]) / len(test_instance.solution_attempts)
                    except:
                        average_score = 0
                    summary = TestSummary(
                        passed=len([attempt for attempt in test_instance.solution_attempts if attempt.passed]),
                        attempts_count=len(test_instance.solution_attempts),
                        average=average_score
                    )
                    return Response(status=200, response=summary.model_dump_json())
            raise Exception('no such test instance in the subject')
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve the test summary", str(e)]))
        
    def _get_student_results(self, subject_id : str):
        try:
            username = request.args['username']
            self._check_subject_teacher(username, subject_id)
            test_id = request.args['test_id']
            remark = request.args['remark']
            for test_instance in self.SUBJECTS_DATABASE[subject_id].test_instances:
                if test_instance.test.info.id == test_id and test_instance.remark == remark:
                    return Response(status=200, response=json.dumps([CheckedAttempt.model_dump_json(attempt) for attempt in test_instance.solution_attempts]))
            raise Exception('no such test instance in the subject')
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve the student result", str(e)]))

    # prefill database

    def _prefill_database(self):
        # subject_id: subject
        self.SUBJECTS_DATABASE = {
            "musterfrau_subject_0": Subject(
                info=SubjectInfo(
                    id="musterfrau_subject_0",
                    name="Math (Group 1)",
                    description="Math is fun",
                    owner="musterfrau",
                    teachers=["musterfrau"],
                ),
                test_instances=[],
                teacher_access_code='teacher1',
                student_access_code="3001",
                students=[]
        ),
            "mmm_subject_0": Subject(
                info=SubjectInfo(
                    id="mmm_subject_0",
                    name="Math (Group 2)",
                    description="Math is fun",
                    owner="mmm",
                    teachers=["mmm", "musterfrau"],
                ),
                test_instances=[],
                teacher_access_code='teacher2',
                student_access_code="tuesday",
                students=[]
            )
        }

        # username : [subject_id]
        self.ID_DATABASE = { 
            "musterfrau": 0,
            "mmm": 0
        }
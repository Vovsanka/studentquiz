import json
from typing import Optional

from flask_cors import CORS
from flask import Flask, Response, request

from test_service.TaskTypes import TaskType, SingleChoiceTask, MultipleChoiceTask
from test_service.TestTypes import Test, TestInfo


class TestService:

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
        self.app.logger.info("TestService inited.")

    def _register_routes(self):
        self.app.route('/test_service/get_my_tests_info', methods=['GET'])(self._get_my_tests_info)
        self.app.route('/test_service/get_all_tests_info', methods=['GET'])(self._get_all_tests_info)
        self.app.route('/test_service/get_test_info/<test_id>', methods=['GET'])(self._get_test_info)
        self.app.route('/test_service/get_test', methods=['GET', 'POST'])(self._create_empty_test)
        self.app.route('/test_service/get_test/<test_id>', methods=['GET'])(self._get_test)
        self.app.route('/test_service/save_test/<test_id>', methods=['PUT'])(self._save_test)
        self.app.route('/test_service/delete_test/<test_id>', methods=['DELETE'])(self._delete_test)

        self.app.before_request(self._before_request)

    def _before_request(self):
        # check service secret
        if request.headers.get('ServiceSecret') != self.app.config["SERVICE_SECRET"]:
            return Response(status=500, response=json.dumps(["Cannot access TestService", "only GatewayAPI may access TestService"]))

    def _init_database(self):
        # Data-structures that simulate a service database
        self.TESTS_DATABASE = dict()
        self.ID_DATABASE = dict()
        # fill database with some entities for testing
        self._prefill_database() 

    

    # helper methods
    def _generate_test_id(self, username):
        if username not in self.ID_DATABASE:
            self.ID_DATABASE[username] = 0
        new_id = self.ID_DATABASE[username] = self.ID_DATABASE[username] + 1
        return f'{username}_test_{new_id}'
    
    ### Test service endpoints

    def _get_my_tests_info(self):
        try:
            username = request.args['username']
            test_dict = self.TESTS_DATABASE.get(username)
            if test_dict is None:
                return Response(response=json.dumps([]))
            return Response(response=json.dumps([test.info.model_dump_json() for test in test_dict.values()]))
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve my tests info", str(e)]))
        
    def _get_all_tests_info(self):
        try:
            tests_info = []
            tests_teachers = []
            for teacher, teacher_tests in self.TESTS_DATABASE.items():
                tests_info += [test.info for test in teacher_tests.values()]
                tests_teachers += [teacher for _ in teacher_tests.values()]
            return Response(response=json.dumps({
                    'tests_info': [info.model_dump_json() for info in tests_info],
                    'tests_teachers': tests_teachers
                }))
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve all tests info", str(e)]))
        

        
    def _get_test_info(self, test_id : str):
        try:
            username = request.args['username']
            if username not in self.TESTS_DATABASE:
                raise Exception('you do not have any tests')
            if test_id not in self.TESTS_DATABASE[username]:
                raise Exception('you do not have this test')
            test_info = self.TESTS_DATABASE[username][test_id].info
            return Response(response=test_info.model_dump_json())
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve the test info", str(e)]))
    
    def _create_empty_test(self):
        try:
            username = request.args['username']
            empty_test = Test(
                info=TestInfo(
                    id=self._generate_test_id(username),
                    name="",
                    description=""
                ),
                tasks = [],
                pass_percents = 50
            )
            # save the empty test
            if username not in self.TESTS_DATABASE:
                self.TESTS_DATABASE[username] = {}
            self.TESTS_DATABASE[username][empty_test.info.id] = empty_test
            return Response(response=empty_test.model_dump_json())
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot create an empty test", str(e)]))

    def _get_test(self, test_id : Optional[str] = None):
        try:
            username = request.args['username']
            if username not in self.TESTS_DATABASE:
                raise Exception('you do not have any tests')
            test = Test.model_validate(self.TESTS_DATABASE[username][test_id])
            return Response(response=test.model_dump_json())
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot retrieve the test", str(e)]))
        
    def _save_test(self, test_id : str):
        try:
            username = request.args['username']
            test = Test.model_validate_json(request.form['test'])
            if username not in self.TESTS_DATABASE:
                self.TESTS_DATABASE[username] = {}
            if test_id not in self.TESTS_DATABASE[username]:
                raise Exception('you do not have this test')
            self.TESTS_DATABASE[username][test_id] = test
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot save the test", str(e)]))
        
    def _delete_test(self, test_id : str):
        try:
            username = request.args['username']
            if username in self.admins:
                for teacher, teacher_tests in self.TESTS_DATABASE.items():
                    if test_id in teacher_tests:
                        del self.TESTS_DATABASE[teacher][test_id]
                        return Response(status=200)
                raise Exception('test not found')
            # delete the test
            if username not in self.TESTS_DATABASE:
                self.TESTS_DATABASE[username] = {}
            if test_id not in self.TESTS_DATABASE[username]:
                raise Exception('you do not have this test')
            del self.TESTS_DATABASE[username][test_id]
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot delete the test", str(e)]))
    
    # prefill database
        
    def _prefill_database(self):
        self.TESTS_DATABASE = {
            "mmm" : {"mmm_test_0" : Test(info=TestInfo(id="mmm_test_0",
                                                name="Mini-Test", 
                                                description="math tests"), 
                                            tasks=[SingleChoiceTask(question="9 * 12 = ?",
                                                                tag="easy",
                                                                options=["96", "108", "120"],
                                                                answer=1,
                                                                points=10,
                                                                type=TaskType.SINGLE_CHOICE),
                                                    SingleChoiceTask(question="3 + 3 * 3 = ?",
                                                                tag="easy",
                                                                options=["9", "18", "12"],
                                                                answer=2,
                                                                points=15,
                                                                type=TaskType.SINGLE_CHOICE),
                                                    MultipleChoiceTask(question="x mod 3 = 1. x?",
                                                                tag="hard",
                                                                options=["988", "254", "1684", "403", "503"],
                                                                answer=[0, 2, 3],
                                                                points=25,
                                                                type=TaskType.MULTIPLE_CHOICE),
                                                    ],
                                            pass_percents=60)}
        }

        self.ID_DATABASE = {
            "mmm": 0
        }
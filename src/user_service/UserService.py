import json

from flask import Flask, Response, request
from flask_cors import CORS

from user_service.UserTypes import User, UserInfo, Credentials, Role 



class UserService:

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
        self.app.logger.info("self.USERService inited!")

    def _register_routes(self):
        self.app.route('/user_service/validate_credentials', methods=['POST', 'GET'])(self._validate_credentials)
        self.app.route('/user_service/register_user', methods=['POST'])(self._register_user)
        self.app.route('/user_service/get_user_info/<username>', methods=['GET'])(self._get_user_info)
        self.app.route('/user_service/get_all_users_info', methods=['GET'])(self._get_all_users_info)
        self.app.route('/user_service/delete_user/<username>', methods=['DELETE'])(self._delete_user)

        self.app.before_request(self._before_request)

    def _before_request(self):
        # check service secret
        if request.headers.get('ServiceSecret') != self.app.config["SERVICE_SECRET"]:
            return Response(status=500, response=json.dumps(["Cannot access UserService", "only GatewayAPI may access UserService"]))
        
    def _init_database(self):
        # Data-structures that simulate a service database
        self.USERS = dict()
        # fill database with some entities for testing
        self._prefill_database() 
    

    # service endpoints

    def _get_user_info(self, username: str):
        try:
            if username not in self.USERS:
                raise Exception('no such User')
            userInfo = self.USERS[username].info
            return Response(response=userInfo.model_dump_json())
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot get the user info", str(e)]))
        
    def _get_all_users_info(self):
        try:
            username = request.args['username']
            if username not in self.admins:
                raise Exception('only admin can manage users!')
            users_info = [user.info for user in self.USERS.values() if user.info.username not in self.admins]
            users_info.sort(key=lambda info: info.username)
            return Response(response=json.dumps([info.model_dump_json() for info in users_info]))
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot get all users info", str(e)]))
        
    def _delete_user(self, username : str):
        try:
            modifier = request.args['username']
            if modifier not in self.admins:
                raise Exception('only admin can delete users!')
            if username not in self.USERS:
                raise Exception('no such user!')
            if username in self.admins:
                raise Exception('impossible to delete admin!')
            del self.USERS[username]
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot delete the user", str(e)]))


    def _validate_credentials(self):
        try:
            credentials = json.loads(request.form['credentials'])
            username = credentials['username']
            password = credentials['password']
            
            if username not in self.USERS or self.USERS[username].credentials.password != password:
                raise Exception ("wrong username or password")
            
            return Response(response=self.USERS[username].info.model_dump_json())
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot log in", str(e)]))

    def _register_user(self):
        try:
            new_user = User.model_validate_json(request.form['user'])
            if new_user.info.role == Role.ADMIN:
                raise Exception('you can not register a new admin')
            if new_user.info.username in self.USERS:
                raise Exception('the username is not available!')
            if not new_user.credentials.username or not new_user.credentials.password:
                raise Exception('username and password cannot be empty')
            self.USERS[new_user.info.username] = new_user
            return Response(status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(status=500, response=json.dumps(["Cannot create a user", str(e)]))

    # prefill database
        
    def _prefill_database(self):
        # Use username as identity and dictionary key
        self.USERS = {
                'admin' : User(
                                info=UserInfo(
                                    username='admin',
                                    name='ADMIN',
                                    role=Role.ADMIN,
                                    token=""),
                                credentials=Credentials(
                                    username='admin',
                                    password='qwerty123'
                                )),
                'alice' : User(
                                info=UserInfo(
                                    username='alice',
                                    name='Alice',
                                    role=Role.STUDENT,
                                    token=""),
                                credentials=Credentials(
                                    username='alice',
                                    password='123'
                                )),
                'mmm': User(
                                info=UserInfo(
                                    username='mmm',
                                    name='Herr Müller',
                                    role=Role.TEACHER,
                                    token=""),
                                credentials=Credentials(
                                    username='mmm',
                                    password='boss'
                                )),
                'musterfrau': User(
                                info=UserInfo(
                                    username='musterfrau',
                                    name='Prof. Musterfrau',
                                    role=Role.TEACHER,
                                    token=""),
                                credentials=Credentials(
                                    username='musterfrau',
                                    password='qwe'
                                ))
        }


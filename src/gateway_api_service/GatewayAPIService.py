import json
from datetime import timedelta

import requests as req

from typing import Optional, Any

from flask_cors import CORS
from flask import Flask, Response, Request, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

from gateway_api_service.UserTypes import UserInfo, Role


class GatewayAPIService:

    def __init__(self, app : Flask, redirect_url : dict, service_secrets : dict):
        self.app = app
        self.redirect_url = redirect_url
        self.service_secrets = service_secrets
        # restrictions
        self.cors = CORS(self.app)
        self.jwt = JWTManager(app)
        # endpoints
        self._endpoint_counter = 1
        self._register_routes()
        # init successfull
        self.app.logger.info("GatewayAPIService inited!")
    
    def _register_routes(self):

        ##user_service

        self.app.route('/frontend_api/get_token', methods=['POST', 'GET'])(self._get_access_token)
        self.app.route('/frontend_api/refresh_token', methods=['GET'])(self._refresh_access_token)

        self._create_endpoint(url='/frontend_api/register_user',
                              methods=['POST'],
                              redirect_host_url=self.redirect_url['user_service'],
                              redirect_root='user_service',
                              secure=False)
    
        self._create_endpoint(url='/frontend_api/get_user_info/<username>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['user_service'],
                              redirect_root='user_service',
                              secure=True,
                              allowed_roles=[Role.STUDENT, Role.TEACHER, Role.ADMIN],
                              provide_username_arg=False)
        
        self._create_endpoint(url='/frontend_api/get_all_users_info',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['user_service'],
                              redirect_root='user_service',
                              secure=True,
                              allowed_roles=[Role.ADMIN],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/delete_user/<username>',
                              methods=['DELETE'],
                              redirect_host_url=self.redirect_url['user_service'],
                              redirect_root='user_service',
                              secure=True,
                              allowed_roles=[Role.ADMIN],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/service_api/get_user_info/<username>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['user_service'],
                              redirect_root='user_service',
                              secure=False,
                              allowed_roles=[Role.STUDENT, Role.TEACHER, Role.ADMIN],
                              retrieve_username_header=False,
                              provide_username_arg=False)

        ### test service

        self._create_endpoint(url='/frontend_api/get_my_tests_info',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['test_service'],
                              redirect_root='test_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/get_all_tests_info',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['test_service'],
                              redirect_root='test_service',
                              secure=True,
                              allowed_roles=[Role.ADMIN],
                              provide_username_arg=True)
       
        self._create_endpoint(url='/frontend_api/get_test_info/<test_id>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['test_service'],
                              redirect_root='test_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/get_test',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['test_service'],
                              redirect_root='test_service',
                              secure=True,
                              allowed_roles=[Role.STUDENT, Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/service_api/get_test/<test_id>',
                      methods=['GET'],
                      redirect_host_url=self.redirect_url['test_service'],
                      redirect_root='test_service',
                      secure=False,
                      retrieve_username_header=True,
                      provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/get_test/<test_id>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['test_service'],
                              redirect_root='test_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/save_test/<test_id>',
                              methods=['PUT'],
                              redirect_host_url=self.redirect_url['test_service'],
                              redirect_root='test_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/delete_test/<test_id>',
                              methods=['DELETE'],
                              redirect_host_url=self.redirect_url['test_service'],
                              redirect_root='test_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER, Role.ADMIN],
                              provide_username_arg=True)
        
        ### subject service

        self._create_endpoint(url='/frontend_api/get_my_subjects_info',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER, Role.STUDENT],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/get_all_subjects_info',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER, Role.STUDENT, Role.ADMIN],
                              provide_username_arg=False)
        
        self._create_endpoint(url='/frontend_api/get_subject_info/<subject_id>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER, Role.STUDENT],
                              provide_username_arg=False)
        
        self._create_endpoint(url='/frontend_api/get_subjects_info_published/<test_id>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/subject_subscribe_teacher/<subject_id>',
                              methods=['POST'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        
        self._create_endpoint(url='/frontend_api/save_test_attempt/<subject_id>',
                              methods=['POST'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.STUDENT],
                              provide_username_arg=True)

        self._create_endpoint(url='/frontend_api/subject_subscribe_student/<subject_id>',
                              methods=['POST'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.STUDENT],
                              provide_username_arg=True)

        self._create_endpoint(url='/frontend_api/get_subject',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/get_subject/<subject_id>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER, Role.STUDENT, Role.ADMIN],
                              provide_username_arg=True)

        self._create_endpoint(url='/frontend_api/save_subject/<subject_id>',
                              methods=['PUT'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/delete_subject/<subject_id>',
                              methods=['DELETE'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER, Role.ADMIN],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/delete_test_instance/<subject_id>',
                              methods=['DELETE'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER, Role.ADMIN],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/publish_test/<subject_id>/<test_id>',
                              methods=['POST'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)    

        self._create_endpoint(url='/frontend_api/remove_teacher_from_subject/<subject_id>/<username>',
                              methods=['DELETE'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/remove_student_from_subject/<subject_id>/<username>',
                              methods=['DELETE'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/get_task_results/<subject_id>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/get_test_summary/<subject_id>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self._create_endpoint(url='/frontend_api/get_student_results/<subject_id>',
                              methods=['GET'],
                              redirect_host_url=self.redirect_url['subject_service'],
                              redirect_root='subject_service',
                              secure=True,
                              allowed_roles=[Role.TEACHER],
                              provide_username_arg=True)
        
        self.app.before_request(self._before_request)

    def _before_request(self):
        # check service_api secret
        root = request.url.removeprefix(request.host_url).split('/')[0]
        if root == 'service_api':
            if request.headers.get('ServiceSecret') != self.service_secrets['service_api']:
                return Response(status=500, response=json.dumps(["Cannot access GatewayAPI", "only services may access GatewayAPI with root /service_api"]))
        elif root != 'frontend_api':
            return Response(status=500, response=json.dumps(["Cannot access GatewayAPI", "unknown request root"]))
        
    def _create_endpoint(self, 
                         url : str,
                         methods: list,
                         redirect_host_url : str,
                         redirect_root : str = "",
                         secure : bool = False,
                         allowed_roles: list[Role] = [],
                         provide_username_arg: bool = False,
                         retrieve_username_header: bool = False):
        
        def redirect_wrapper(request : Request, username_arg : Optional[str] = None):
                redirect_kwargs = {
                        'caller_request': request,
                        'redirect_host_url': redirect_host_url,
                        'redirect_root': redirect_root
                    }
                if retrieve_username_header:
                    username_arg = request.headers['username']
                if provide_username_arg:
                    redirect_kwargs['username_arg'] = username_arg
                return self._redirect(**redirect_kwargs)
    
        if secure:
            @jwt_required()
            def security_endpoint(**kwargs):
                identity = get_jwt_identity()
                user_role = Role(identity[0])
                username = identity[1]
                if user_role in allowed_roles:
                    return redirect_wrapper(request, username_arg=username)
                else:
                    return Response(status='403', response=json.dumps(["Access forbidden", 'the user does not have rights for this operation']))  
            endpoint = security_endpoint
        else:
            def redirect_endpoint(**kwargs):
                return redirect_wrapper(request)
            endpoint = redirect_endpoint

        self.app.route(url, methods=methods, endpoint=f'endpoint_{self._endpoint_counter}')(endpoint)
        self._endpoint_counter += 1
    

    def _redirect(self,
                  caller_request: Request,
                  redirect_host_url : str,
                  redirect_root : str = "",
                  username_arg : Optional[str] = None):
        try:
            caller_root = caller_request.url.removeprefix(caller_request.host_url).split('/')[0]
            # build the redirect url with the username argument
            url = redirect_host_url + '/'
            if redirect_root:
                url += redirect_root
            url += caller_request.url.removeprefix(caller_request.host_url + caller_root)
            if username_arg is not None:
                if '?' in url:
                    url += '&'
                else:
                    url += '?'
                url += 'username=' + username_arg
            if not caller_request.form:
                resp = req.request(caller_request.method, url, headers={'ServiceSecret': self.service_secrets[redirect_root]}, verify=False)
                return Response(response=resp.text,
                                status=resp.status_code)
            else:
                resp = req.request(caller_request.method, url, headers={'ServiceSecret': self.service_secrets[redirect_root]}, data=caller_request.form, verify=False)
                return Response(response=resp.text,
                                status=resp.status_code)
        except Exception as e:
            self.app.logger.error(e)
            return Response(response=json.dumps(['Backend redirecting error', str(e)]), status=500)

    ### Service Endpoints

    def _get_access_token(self):
        try: 
            ### get name and role from the UserService
            user_service_url = self.redirect_url['user_service']
            response = req.post(user_service_url + '/user_service/validate_credentials',
                                headers={'ServiceSecret': self.service_secrets['user_service']},
                                data=request.form,
                                verify=False)
            if response.status_code != 200:
                raise Exception(response.text)
        except Exception as e:
            self.app.logger.error(e)
            return Response(response=str(e), status=500)
        try:
            user_info = UserInfo.model_validate_json(response.text)
            # create userInfo object for the frontend
            user_info.token = create_access_token(identity=(user_info.role, user_info.username),
                                                  expires_delta=timedelta(minutes=15))
            return Response(response=user_info.model_dump_json(), status=200)
        except Exception as e:
            self.app.logger.error(e)
            return Response(response=json.dumps(['Login error', str(e)]), status=500)

    @jwt_required()    
    def _refresh_access_token(self):
        try: 
            new_token = create_access_token(identity=get_jwt_identity(),
                                                  expires_delta=timedelta(minutes=25))
            return Response(response=json.dumps(new_token))
        except Exception as e:
            self.app.logger.error(e)
            return Response(response=json.dumps(['Token refresh error', str(e)]), status=500)

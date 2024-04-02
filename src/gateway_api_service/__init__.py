import os

from dotenv import load_dotenv
from flask import Flask

from .GatewayAPIService import GatewayAPIService


load_dotenv()

user_service_host = os.getenv('USER_SERVICE_HOST')
user_service_port = os.getenv('USER_SERVICE_PORT')
if user_service_host == None:
    user_service_host = 'user_service'

test_service_host = os.getenv('TEST_SERVICE_HOST')
test_service_port = os.getenv('TEST_SERVICE_PORT')
if test_service_host == None:
    test_service_host = 'test_service'

subject_service_host = os.getenv('SUBJECT_SERVICE_HOST')
subject_service_port = os.getenv('SUBJECT_SERVICE_PORT')
if subject_service_host == None:
    subject_service_host = 'subject_service'

redirect_url = { 
            'user_service': f'https://{user_service_host}:{user_service_port}',
            'test_service': f'https://{test_service_host}:{test_service_port}',
            'subject_service': f'https://{subject_service_host}:{subject_service_port}'
        }

service_secrets = {
    'user_service': os.getenv('USER_SERVICE_SECRET'),
    'test_service': os.getenv('TEST_SERVICE_SECRET'),
    'subject_service': os.getenv('SUBJECT_SERVICE_SECRET'),
    'service_api': os.getenv('SERVICE_API_SECRET')
}

app = Flask('GatewayAPIService')
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')

gateway_api_service = GatewayAPIService(app, redirect_url, service_secrets)

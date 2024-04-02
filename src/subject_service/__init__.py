import os

from dotenv import load_dotenv
from flask import Flask

from .SubjectService import SubjectService


load_dotenv()
service_api_host = os.getenv('SERVICE_API_HOST')
service_api_port = os.getenv('SERVICE_API_PORT')
if service_api_host == None:
    service_api_host = 'gateway_api'
service_api_url = f'https://{service_api_host}:{service_api_port}'


app = Flask('SubjectService')
app.config["SERVICE_SECRET"] = os.getenv('SERVICE_SECRET')
app.config["SERVICE_API_SECRET"] = os.getenv('SERVICE_API_SECRET')
subject_service = SubjectService(app, service_api_url)




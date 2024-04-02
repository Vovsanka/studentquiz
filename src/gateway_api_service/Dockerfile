FROM python:3.12-alpine

WORKDIR /gateway_api_service

ENV FLASK_APP=__init__.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
CMD ["flask", "run", "--port=5000", "--cert=cert.pem", "--key=key.pem"]
FROM python:3.6.3-stretch
ADD ./app /code/app
ADD ./requirements.txt /code
WORKDIR /code
RUN pip install -r requirements.txt

EXPOSE 443
EXPOSE 8080
FROM python:3.6.3-stretch
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
# CMD ["python", "app.py"]
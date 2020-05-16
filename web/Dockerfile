FROM python:3.8.3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get install -y vim \
    postgresql-client && \
    mkdir /code
COPY . /code/
WORKDIR /code
RUN pip install -r requirements.txt
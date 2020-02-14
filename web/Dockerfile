FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get install -y supervisor && \
    mkdir /code
COPY requirements.txt /code/
COPY . /code/
WORKDIR /code
RUN pip install -r requirements.txt

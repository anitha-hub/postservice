FROM python:3.8-alpine

MAINTAINER Danfishel Private Ltd

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY . /app

EXPOSE 5002

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
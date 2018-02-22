FROM python:3.5
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=homeconsole
ENV FLASK_DEBUG=1

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code
RUN pip install -r requirements.txt
ADD . /code/
RUN pip install -e .

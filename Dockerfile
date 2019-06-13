FROM python:3.7

ARG project_name=bitchart

VOLUME /opt/$project_name
VOLUME /var/log/$project_name
VOLUME /run/$project_name

ADD requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /opt/$project_name

CMD ["gunicorn", "--bind", "unix:/run/bitchart/gunicorn.sock", "app:app"]
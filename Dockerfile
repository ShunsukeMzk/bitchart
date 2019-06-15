FROM python:3.7

ARG app_name

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

WORKDIR /opt/$app_name

CMD /bin/bash
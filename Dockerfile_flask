FROM python:3.8-alpine

RUN adduser -D app_user
WORKDIR /home/app_user
COPY requirements.txt requirements.txt

RUN python -m venv env
RUN env/bin/pip install -U pip

RUN \
 apk add --no-cache gcc musl-dev libffi-dev  openssl-dev make && \
 apk add --no-cache --virtual .build-deps gcc musl-dev


RUN env/bin/pip install -r requirements.txt

COPY myapp myapp

COPY webapp.py boot.sh ./

RUN chmod +x boot.sh

RUN chown -R app_user:app_user ./
USER app_user

EXPOSE 5555
ENTRYPOINT ["./boot.sh"]

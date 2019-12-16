FROM python:3.6 as base

COPY ./bin/s6-overlay-amd64.tar.gz /tmp/s6-overlay-amd64.tar.gz

RUN tar xvfz /tmp/s6-overlay-amd64.tar.gz -C / \
    && rm -f /tmp/s6-overlay-amd64.tar.gz \
    && adduser --disabled-password --gecos '' celery

RUN apt-get update \
    && apt-get install -y locales \
    && sed -i -e 's/# pl_PL.UTF-8 UTF-8/pl_PL.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen

ENTRYPOINT ["/init"]

WORKDIR /srv/app

####################################################################################

FROM base as builder

WORKDIR /srv/app

RUN pip3 install --no-cache-dir gunicorn

COPY ./src/requirements.txt /srv/app/requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src/ /srv/app/

RUN python3 -m compileall -b .

EXPOSE 8000

CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:8000", "meetup_bot.wsgi:application"]

FROM python:3-stretch

RUN useradd sinker

WORKDIR /var/code
ADD . .

RUN chown -R sinker /var/code && \
    pip3 install -r requirements.txt

USER sinker

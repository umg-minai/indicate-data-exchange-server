FROM python:3.13-slim-trixie

COPY requirements.txt              /app/
COPY indicate_data_exchange_server /app/indicate_data_exchange_server/

WORKDIR /app

RUN pip install --root-user-action=ignore -r requirements.txt

COPY --chmod=760 run-server.sh /app/

ARG DATABASE_HOST
ARG DATABASE_POST
ARG DATABASE_NAME
ARG DATABASE_USER
# Password should be provided via a secret as /run/secrets/database-password
ARG DATABASE_SCHEMA

ENV LISTEN_ADDRESS=0.0.0.0
ENV LISTEN_PORT=8080

EXPOSE ${LISTEN_PORT}

CMD [ "/app/run-server.sh" ]

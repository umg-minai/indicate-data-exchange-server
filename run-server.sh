#!/bin/bash

PYTHONPATH=/app                                         \
DATABASE_PASSWORD=$(cat /run/secrets/database-password) \
  exec uvicorn indicate_data_exchange_server.main:app   \
         --host ${LISTEN_ADDRESS} --port ${LISTEN_PORT}

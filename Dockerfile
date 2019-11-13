FROM python:3.6-alpine

RUN apk add --no-cache linux-headers musl-dev gcc tzdata postgresql-dev libstdc++ git && \
    rm -rf /var/cache/apk/* && \
    pip install virtualenv

ENV VENV_PATH /home/pyuser/.venv

ARG USER_ID
ARG GROUP_ID

RUN addgroup -g $GROUP_ID pyuser && \
    adduser -h /home/pyuser -u $USER_ID -D -G pyuser pyuser && \
    mkdir -p /home/pyuser/.vscode-server && \
    mkdir -p /home/pyuser/.cache && \
    mkdir -p ${VENV_PATH} && \
    chown pyuser:pyuser -R /home/pyuser
    
WORKDIR /app

USER pyuser

RUN virtualenv ${VENV_PATH}

ENV PATH ${VENV_PATH}/bin:$PATH

CMD exec /bin/sh -c "trap : TERM INT; (while true; do sleep 1000; done) & wait"
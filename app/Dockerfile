FROM amsterdam/python:3.9-buster
LABEL maintainer="datapunt@amsterdam.nl"

ENV PYTHONUNBUFFERED 1
ARG ONDERHUUR_MODEL_CREDS
ARG ONDERHUUR_MODEL_PERSONAL_ACCESS_TOKEN

# Setup Certificates for ADP/Motiv
COPY certificates/adp_rootca.crt /usr/local/share/ca-certificates/extras/adp_rootca.crt
RUN chmod 644 /usr/local/share/ca-certificates/extras/adp_rootca.crt \
  && update-ca-certificates --fresh

# Setup datapunt directories and user
RUN adduser --system datapunt
ENV DIRECTORYLIST "/static /app /downloads /certificates /deploy /var/log/uwsgi /fraud_prediction_cache"
RUN mkdir -p ${DIRECTORYLIST} && chown datapunt ${DIRECTORYLIST}

# Setup application
WORKDIR /app
COPY requirements.txt /app/

RUN mkdir /tmp/onderhuur_model

# Clone the private cto-onderhuur library using a deploy token
RUN if [ "x$ONDERHUUR_MODEL_CREDS" = "x" ] ; then echo ONDERHUUR_MODEL_CREDS not provided ; else git clone -b bwv_branch --single-branch https://${ONDERHUUR_MODEL_CREDS}@git.data.amsterdam.nl/cto-fraude-aanpak/onderhuur-adreskwaliteit-backend /tmp/onderhuur_model ; fi

RUN apt-get update && apt-get install -y
RUN pip install --upgrade pip
RUN pip install uwsgi
RUN pip install --no-cache-dir -r requirements.txt

RUN if [ "x$ONDERHUUR_MODEL_CREDS" = "x" ] ; then echo ONDERHUUR_MODEL_CREDS not provided ; else pip install --no-cache-dir /tmp/onderhuur_model ; fi

RUN pip install -I shap==0.38.1

COPY . /app/
COPY deploy /deploy/

RUN chmod +x /app/wait-for.sh
RUN chmod +x /app/celery.sh
RUN chmod +x /app/celery-beat.sh

CMD ["/deploy/entrypoint.sh"]

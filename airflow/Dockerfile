FROM apache/airflow:2.5.0
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
         nano \
         jq \
         curl \
         git \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow
COPY ./requirements.txt /requirements.txt
RUN pip --no-cache-dir install -r /requirements.txt

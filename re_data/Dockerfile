FROM python:3.9-slim

RUN apt-get -y update && apt-get install -y git

RUN pip install --no-cache-dir re_data dbt-core dbt-postgres

EXPOSE 8085

ENTRYPOINT [ "/bin/bash" ]

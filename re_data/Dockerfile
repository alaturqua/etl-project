FROM python:3.9-slim

RUN pip install --no-cache-dir re_data dbt-core dbt-postgres

COPY ./sql-dbt /sql-dbt

WORKDIR /sql-dbt

EXPOSE 8050

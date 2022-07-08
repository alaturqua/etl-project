#!/bin/bash
cd "$(dirname "$0")"

dbt clean
dbt deps
dbt run
dbt test
re_data run --start-date $(date '+%Y-%m-%d' -d '7 days ago') --end-date $(date '+%Y-%m-%d') --full-refresh --interval days:1
re_data overview generate
re_data overview serve

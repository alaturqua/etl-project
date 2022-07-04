
{{
    config(
        re_data_monitored=true,
        re_data_time_filter='ts',
    )
}}

select *
from {{ source('public', 'timesheet') }}
{{
    config(
        re_data_monitored=true,
        re_data_time_filter='date_ts',
		re_data_anomaly_detector={'name': 'z_score', 'threshold': 3},

    )
}}


with base as (
	select
		distinct user_name,
		ts::date as date_ts,
		date_part('year', ts) as year_ts,
		date_part('month', ts) as month_ts,
		date_part('day', ts) as day_ts,
		date_part('week', ts) as week_of_year,
		to_char(ts, 'month') as month_name,
		to_char(ts, 'day') as day_of_week,
		max(ts) OVER (PARTITION BY user_name, ts :: date) as end_time,
		min(ts) OVER (PARTITION BY user_name, ts :: date) as start_time
	from
		{{ ref('stg_timesheet') }}
	where
	1=1
	 and user_name = 'U0397S7U1FH'
	 and user_message not like '%sick%' 
	 and user_message not like '%vacation%' 
	 and user_message not like '%holiday%'
	 and user_message not like '%off%'
	order by
		date_ts desc
), prep AS (
select
	user_name,
	date_ts,
	year_ts,
	month_ts,
	day_ts,
	day_of_week,
	week_of_year,
	month_name,
	start_time,
	end_time,
	abs(extract( epoch from end_time - start_time)/3600) - 1 as working_hours,
	abs(extract( epoch from end_time - start_time)/3600) - 9 as over_time
from
	base
order by 2 desc
), final as (
	select 
	*,
	sum(over_time) over (partition by user_name order by date_ts) as cum_over_time
	from prep
)

select * from final
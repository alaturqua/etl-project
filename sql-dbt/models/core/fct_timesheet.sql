with final as (
	select
		distinct user_name,
		ts :: date as date_ts,
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
		user_name = 'U0397S7U1FH'
	order by
		date_ts desc
)
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
	age(end_time, start_time) as working_hours,
	age(end_time, start_time) - interval '8 hours' as over_time
from
	final
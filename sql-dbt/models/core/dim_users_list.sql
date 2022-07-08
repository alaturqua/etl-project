select 
id,
name,
real_name,
ts
from
{{ ref('stg_users_list') }}
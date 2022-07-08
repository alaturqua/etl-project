select *
from {{ source('public', 'users_list') }}
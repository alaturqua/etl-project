

select 
to_date(tag::text, 'DD.MM.YYYY') as tag,
feiertage,
bundesland,
to_char(to_date(tag::text, 'DD.MM.YYYY'), 'day') as day_of_week
from 
    {{ ref('bayern_feiertage') }} 
with households as (

    select
        household_id,
        region,
        timezone
    from {{ ref('stg_households') }}

)

select
    household_id as household_key,
    household_id,
    region,
    timezone
from households
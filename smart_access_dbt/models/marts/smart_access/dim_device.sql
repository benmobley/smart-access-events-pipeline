with devices as (

    select
        device_id,
        household_id,
        device_type,
        model,
        firmware_version,
        installed_at::date as installed_date
    from {{ ref('stg_devices') }}

),

deduped as (

    select
        device_id,
        household_id,
        device_type,
        model,
        firmware_version,
        installed_date,
        row_number() over (
            partition by device_id
            order by installed_date desc
        ) as row_num
    from devices

)

select
    device_id           as device_key,   -- dimension key
    device_id,
    household_id,
    device_type,
    model,
    firmware_version,
    installed_date
from deduped
where row_num = 1
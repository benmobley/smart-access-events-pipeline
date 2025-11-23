with source as (

    select *
    from {{ source('smart_access', 'raw_device_health') }}

),

renamed as (

    select
        device_id,
        reported_at::timestamp as reported_at,
        battery_pct::numeric as battery_pct,
        signal_strength_dbm::numeric as signal_strength_dbm,
        is_online::boolean as is_online
    from source

)

select * from renamed
with source as (

    select * 
    from {{ source('smart_access', 'raw_access_events') }}

),

renamed as (

    select
        event_id,
        device_id,
        user_id,
        event_type,
        trigger_source,
        created_at::timestamp as event_ts,
        lat,
        lon
    from source

)

select * from renamed
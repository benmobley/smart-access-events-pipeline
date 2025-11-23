with events as (

    select
        event_id,
        device_id,
        user_id,
        event_type,
        trigger_source,
        event_ts,
        lat,
        lon
    from {{ ref('stg_access_events') }}

),

joined as (

    select
        e.event_id,
        e.event_ts,
        e.device_id,
        d.device_key,
        d.household_id,
        h.household_key,
        e.user_id,
        e.event_type,
        e.trigger_source,
        e.lat,
        e.lon,
        d.device_type,
        d.model,
        d.firmware_version,
        h.region,
        h.timezone
    from events e
    left join {{ ref('dim_device') }} d
      on e.device_id = d.device_id
    left join {{ ref('dim_household') }} h
      on d.household_id = h.household_id
)

select * from joined
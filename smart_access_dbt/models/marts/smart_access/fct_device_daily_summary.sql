with events as (

    select
        device_id,
        date_trunc('day', event_ts) as event_date,
        count(*) as total_events,
        count(*) filter (where event_type = 'open') as opens,
        count(*) filter (where event_type = 'close') as closes,
        count(*) filter (where event_type = 'command_failed') as failures
    from {{ ref('fct_access_events') }}
    group by device_id, event_date

),

health as (

    select
        device_id,
        date_trunc('day', reported_at) as health_date,
        avg(battery_pct) as avg_battery_pct,
        avg(signal_strength_dbm) as avg_signal_strength_dbm,
        avg(case when is_online then 1.0 else 0.0 end) as online_ratio
    from {{ ref('stg_device_health') }}
    group by device_id, health_date

),

joined as (

    select
        e.device_id,
        e.event_date as date,
        e.total_events,
        e.opens,
        e.closes,
        e.failures,
        coalesce(h.avg_battery_pct,  null) as avg_battery_pct,
        coalesce(h.avg_signal_strength_dbm, null) as avg_signal_strength_dbm,
        coalesce(h.online_ratio, null) as online_ratio
    from events e
    left join health h
      on e.device_id = h.device_id
     and e.event_date = h.health_date
)

select * from joined
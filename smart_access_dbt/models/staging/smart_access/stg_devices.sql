with source as (

    select * 
    from {{ source('smart_access', 'raw_devices') }}

),

renamed as (

    select
        device_id,
        household_id,
        device_type,
        model,
        firmware_version,
        installed_at::timestamp as installed_at
    from source

)

select * from renamed
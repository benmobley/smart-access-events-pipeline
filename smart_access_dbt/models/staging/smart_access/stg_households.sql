with source as (

    select *
    from {{ source('smart_access', 'raw_households') }}

),

renamed as (

    select
        household_id,
        region,
        timezone
    from source

)

select * from renamed
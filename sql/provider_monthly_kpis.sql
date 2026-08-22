-- BI-ready provider/month fact model.
-- Expected source table: stg_ae_activity

with monthly as (
    select
        provider_code,
        max(provider_name) as provider_name,
        date_trunc('month', month) as month,
        sum(attendances) as attendances,
        sum(within_4h) as within_4h,
        sum(attendances - within_4h) as breaches_4h,
        sum(emergency_admissions) as emergency_admissions
    from stg_ae_activity
    group by 1, 3
),
scored as (
    select
        *,
        within_4h * 1.0 / nullif(attendances, 0) as four_hour_rate,
        breaches_4h * 1.0 / nullif(attendances, 0) as breach_rate,
        lag(attendances) over (partition by provider_code order by month) as prior_month_attendances
    from monthly
)
select
    *,
    (attendances - prior_month_attendances) * 1.0 / nullif(prior_month_attendances, 0) as attendance_mom_pct
from scored;

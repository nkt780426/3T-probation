with dim_engage_date as (
    SELECT DISTINCT
        DATE_ADD('1970-01-01', INTERVAL engage_date DAY) AS engage_date,
        YEAR(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS year,
        MONTH(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS month,
        DAY(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS day,
        QUARTER(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS quarter,
        DAYNAME(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS day_of_week
    FROM report.sales_pipeline
    WHERE engage_date IS NOT NULL
)

select * from dim_engage_date
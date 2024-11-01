with dim_close_date as (
    SELECT DISTINCT
        DATE_ADD('1970-01-01', INTERVAL close_date DAY) AS close_date,
        YEAR(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS year,
        MONTH(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS month,
        DAY(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS day,
        QUARTER(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS quarter,
        DAYNAME(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS day_of_week
    FROM report.sales_pipeline
    WHERE close_date IS NOT NULL
)

select * from dim_close_date
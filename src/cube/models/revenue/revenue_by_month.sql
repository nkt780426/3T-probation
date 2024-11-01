SELECT 
    YEAR(ed.engage_date) AS year,
    MONTH(ed.engage_date) AS month,
    SUM(sp.close_value) AS total_revenue
FROM 
    {{ ref('fact_sales_pipeline') }} sp
JOIN 
    {{ ref('dim_engage_date') }} ed ON sp.engage_date = ed.engage_date
WHERE 
    sp.close_date IS NOT NULL
GROUP BY 
    YEAR(ed.engage_date), MONTH(ed.engage_date)
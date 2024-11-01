SELECT 
    YEAR(ed.engage_date) AS year,
    QUARTER(ed.engage_date) AS quarter,
    SUM(sp.close_value) AS total_revenue
FROM 
    {{ ref('fact_sales_pipeline') }} sp
JOIN 
    {{ ref('dim_engage_date') }} ed ON sp.engage_date = ed.engage_date
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    YEAR(ed.engage_date), QUARTER(ed.engage_date)
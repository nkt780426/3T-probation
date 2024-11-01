SELECT 
    a.account AS account,
    SUM(sp.close_value) AS total_revenue
FROM 
    {{ ref('fact_sales_pipeline') }} sp
JOIN 
    {{ ref('dim_account') }} a ON sp.account = a.account
WHERE 
    sp.close_date IS NOT NULL
GROUP BY 
    a.account

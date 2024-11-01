SELECT 
    p.product AS product,
    SUM(sp.close_value) AS total_revenue
FROM 
    {{ ref('fact_sales_pipeline') }} sp
JOIN 
    {{ ref('dim_product') }} p ON sp.product = p.product
WHERE 
    sp.close_date IS NOT NULL
GROUP BY 
    p.product
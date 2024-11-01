SELECT 
    p.product AS product,
    a.sector AS sector,
    SUM(sp.close_value) AS total_revenue
FROM 
    {{ ref('fact_sales_pipeline') }} sp
JOIN 
    {{ ref('dim_product') }} p ON sp.product = p.product
JOIN 
    {{ ref('dim_account') }} a ON sp.account = a.account
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    p.product, a.sector
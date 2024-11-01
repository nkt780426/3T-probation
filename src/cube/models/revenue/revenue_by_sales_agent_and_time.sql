SELECT 
    st.sales_agent AS sales_agent,
    ed.engage_date AS engage_date,
    SUM(sp.close_value) AS total_revenue
FROM 
    {{ ref('fact_sales_pipeline') }} sp
JOIN 
    {{ ref('dim_sales_team') }} st ON sp.sales_agent = st.sales_agent
JOIN 
    {{ ref('dim_engage_date') }} ed ON sp.engage_date = ed.engage_date
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    st.sales_agent, ed.engage_date

SELECT 
    st.manager AS manager,
    SUM(sp.close_value) AS total_revenue
FROM 
    {{ ref('fact_sales_pipeline') }} sp
JOIN 
    {{ ref('dim_sales_team') }} st ON sp.sales_agent = st.sales_agent
WHERE 
    sp.close_date IS NOT NULL
GROUP BY 
    st.manager
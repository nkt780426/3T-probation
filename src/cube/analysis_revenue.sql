--View Doanh Thu Theo Thời Gian
CREATE VIEW revenue_by_time AS
SELECT 
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp;

--View Tổng Doanh Thu Theo Từng Sản Phẩm
CREATE VIEW revenue_by_product AS
SELECT 
    p.product AS product,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_product p ON sp.product = p.product
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    p.product;

--View Tổng Doanh Thu Theo Từng Đội Ngũ Bán Hàng
CREATE VIEW revenue_by_sales_agent AS
SELECT 
    st.sales_agent AS sales_agent,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_sales_team st ON sp.sales_agent = st.sales_agent
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    st.sales_agent;

--View Doanh Thu Theo Từng Công Ty
CREATE VIEW revenue_by_account AS
SELECT 
    a.account AS account,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_account a ON sp.account = a.account
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    a.account;

--View Doanh Thu Theo Ngành
CREATE VIEW revenue_by_sector AS
SELECT 
    a.sector AS sector,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_account a ON sp.account = a.account
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    a.sector;

--View Doanh Thu Theo Dòng Sản Phẩm
CREATE VIEW revenue_by_product_series AS
SELECT 
    p.series AS product_series,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_product p ON sp.product = p.product
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    p.series;

--View Doanh Thu Theo Quản Lý Bán Hàng
CREATE VIEW revenue_by_manager AS
SELECT 
    st.manager AS manager,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_sales_team st ON sp.sales_agent = st.sales_agent
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    st.manager;

--View Doanh Thu Theo Thời Gian (Theo Tháng)
CREATE VIEW revenue_by_month AS
SELECT 
    YEAR(ed.engage_date) AS year,
    MONTH(ed.engage_date) AS month,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_engage_date ed ON sp.engage_date = ed.engage_date
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    YEAR(ed.engage_date), MONTH(ed.engage_date);

--View Doanh Thu Theo Quý
CREATE VIEW revenue_by_quarter AS
SELECT 
    YEAR(ed.engage_date) AS year,
    QUARTER(ed.engage_date) AS quarter,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_engage_date ed ON sp.engage_date = ed.engage_date
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    YEAR(ed.engage_date), QUARTER(ed.engage_date);

--View Doanh Thu Theo Ngày

CREATE VIEW revenue_by_day AS
SELECT 
    ed.engage_date AS engage_date,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_engage_date ed ON sp.engage_date = ed.engage_date
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    ed.engage_date;

--View Doanh Thu Tổng Hợp Theo Sản Phẩm và Ngành
CREATE VIEW revenue_by_product_and_sector AS
SELECT 
    p.product AS product,
    a.sector AS sector,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_product p ON sp.product = p.product
JOIN 
    dim_account a ON sp.account = a.account
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    p.product, a.sector;

--View Doanh Thu Tổng Hợp Theo Đội Ngũ Bán Hàng và Thời Gian
CREATE VIEW revenue_by_sales_agent_and_time AS
SELECT 
    st.sales_agent AS sales_agent,
    ed.engage_date AS engage_date,
    SUM(sp.close_value) AS total_revenue
FROM 
    fact_sales_pipeline sp
JOIN 
    dim_sales_team st ON sp.sales_agent = st.sales_agent
JOIN 
    dim_engage_date ed ON sp.engage_date = ed.engage_date
WHERE 
    sp.close_date IS NOT NULL  -- Chỉ tính doanh thu đã hoàn tất
GROUP BY 
    st.sales_agent, ed.engage_date;

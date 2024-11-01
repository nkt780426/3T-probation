USE data_mart;

-- Account Dimension Table
CREATE VIEW dim_account AS
SELECT 
    account AS account,
    sector AS sector,
    year_established AS year_established,
    revenue AS revenue,
    employees AS employees,
    office_location AS office_location,
    subsidiary_of AS subsidiary_of
FROM report.accounts;

-- Product Dimension Table
CREATE VIEW dim_product AS
SELECT 
    product AS product,
    series AS series,
    sales_price AS sales_price
FROM report.products;

-- Sales Team Dimension Table
CREATE VIEW dim_sales_team AS
SELECT 
    sales_agent AS sales_agent,
    manager AS manager,
    regional_office AS regional_office
FROM report.sales_teams;

-- Deal Stage Dimension Table
CREATE VIEW dim_deal_stage AS
SELECT DISTINCT 
    deal_stage AS deal_stage_name
FROM report.sales_pipeline;

-- Engage Date Dimension Table
CREATE VIEW dim_engage_date AS
SELECT DISTINCT
    DATE_ADD('1970-01-01', INTERVAL engage_date DAY) AS engage_date,
    YEAR(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS year,
    MONTH(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS month,
    DAY(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS day,
    QUARTER(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS quarter,
    DAYNAME(DATE_ADD('1970-01-01', INTERVAL engage_date DAY)) AS day_of_week
FROM report.sales_pipeline
WHERE engage_date IS NOT NULL;

-- Close Date Dimension Table
CREATE VIEW dim_close_date AS
SELECT DISTINCT
    DATE_ADD('1970-01-01', INTERVAL close_date DAY) AS close_date,
    YEAR(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS year,
    MONTH(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS month,
    DAY(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS day,
    QUARTER(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS quarter,
    DAYNAME(DATE_ADD('1970-01-01', INTERVAL close_date DAY)) AS day_of_week
FROM report.sales_pipeline
WHERE close_date IS NOT NULL;

-- Sales Pipeline Fact Table
CREATE VIEW fact_sales_pipeline AS
SELECT 
    opportunity_id AS opportunity_id,
    (SELECT account FROM report.accounts WHERE report.accounts.account = report.sales_pipeline.account) AS account,
    (SELECT product FROM report.products WHERE report.products.product = report.sales_pipeline.product) AS product,
    (SELECT sales_agent FROM report.sales_teams WHERE report.sales_teams.sales_agent = report.sales_pipeline.sales_agent) AS sales_agent,
    (SELECT deal_stage_name FROM dim_deal_stage WHERE dim_deal_stage.deal_stage_name = report.sales_pipeline.deal_stage) AS deal_stage,
    DATE(FROM_UNIXTIME(engage_date * 86400)) AS engage_date,
    DATE(FROM_UNIXTIME(close_date * 86400)) AS close_date,
    close_value AS close_value
FROM report.sales_pipeline;

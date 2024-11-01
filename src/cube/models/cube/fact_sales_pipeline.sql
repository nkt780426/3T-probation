SELECT 
    opportunity_id AS opportunity_id,
    (SELECT account FROM report.accounts WHERE report.accounts.account = report.sales_pipeline.account) AS account,
    (SELECT product FROM report.products WHERE report.products.product = report.sales_pipeline.product) AS product,
    (SELECT sales_agent FROM report.sales_teams WHERE report.sales_teams.sales_agent = report.sales_pipeline.sales_agent) AS sales_agent,
    (SELECT deal_stage_name FROM {{ ref('dim_deal_stage') }} WHERE deal_stage_name = report.sales_pipeline.deal_stage) AS deal_stage,
    DATE(FROM_UNIXTIME(engage_date * 86400)) AS engage_date,
    DATE(FROM_UNIXTIME(close_date * 86400)) AS close_date,
    close_value AS close_value
FROM report.sales_pipeline
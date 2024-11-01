with dim_deal_stage as (
    SELECT DISTINCT 
        deal_stage AS deal_stage_name
    FROM report.sales_pipeline
)

SELECT * FROM dim_deal_stage
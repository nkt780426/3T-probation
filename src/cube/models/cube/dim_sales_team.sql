with dim_sales_team as (
    SELECT 
        sales_agent AS sales_agent,
        manager AS manager,
        regional_office AS regional_office
    FROM report.sales_teams
)

SELECT * FROM dim_sales_team
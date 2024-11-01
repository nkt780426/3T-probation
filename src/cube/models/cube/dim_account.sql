with dim_account as(
    SELECT 
        account AS account,
        sector AS sector,
        year_established AS year_established,
        revenue AS revenue,
        employees AS employees,
        office_location AS office_location,
        subsidiary_of AS subsidiary_of
    FROM report.accounts
)

select * from dim_account
with dim_product as (
    SELECT 
        product AS product,
        series AS series,
        sales_price AS sales_price
    FROM report.products
)

select * from dim_product
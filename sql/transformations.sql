/* ================================================================================
PROJECT: Supply Chain Data Warehouse (Medallion Architecture)
DESCRIPTION: ETL process from Bronze (Raw) to Silver (Clean) to Gold (Analytics).
================================================================================
*/

-- -----------------------------------------------------------------------------
-- LAYER: SILVER (Data Cleaning & Standardization)
-- -----------------------------------------------------------------------------

CREATE OR REPLACE VIEW silver_product_master AS 
SELECT DISTINCT
    REPLACE(sku, ' ', '') AS sku,
    TRIM(productname) AS productname,
    category,
    subcategory,
    brand,
    CAST(standardcost AS NUMERIC(10,2)) AS standardcost,
    CAST(standardprice AS NUMERIC(10,2)) AS standardprice,
    launchdate,
    discontinuationdate,
    status,
    preferredsupplier,
    unitofmeasure
FROM bronze_product_master;

CREATE OR REPLACE VIEW silver_store_master AS 
SELECT DISTINCT
    TRIM(storeid) AS storeid,
    TRIM(storename) AS storename,
    TRIM(region) AS region,
    TRIM(city) AS city,
    CAST(openingdate AS DATE) AS openingdate,
    TRIM(storetype) AS storetype,
    TRIM(storemanager) AS storemanager
FROM bronze_store_master;

CREATE OR REPLACE VIEW silver_supplier_master AS 
SELECT DISTINCT
    TRIM(supplierid) AS supplierid,
    TRIM(suppliername) AS suppliername,
    TRIM(country) AS country,
    CAST(leadtimedays AS INTEGER) AS leadtimedays,
    CAST(reliabilityscore AS NUMERIC(3,2)) AS reliabilityscore,
    CAST(contractstartdate AS DATE) AS contractstartdate,
    TRIM(paymentterms) AS paymentterms,
    TRIM(suppliercategory) AS suppliercategory
FROM bronze_supplier_master;

CREATE OR REPLACE VIEW silver_sales_transactions AS 
SELECT DISTINCT
    TRIM(invoiceid) AS invoiceid,
    CAST(orderdate AS DATE) AS orderdate,
    TRIM(storename) AS storename,
    TRIM(region) AS region,
    REPLACE(sku, ' ', '') AS sku,
    TRIM(productname) AS productname,
    TRIM(category) AS category,
    TRIM(suppliername) AS suppliername,
    CAST(quantitysold AS INTEGER) AS quantitysold,
    CAST(unitprice AS NUMERIC(10,2)) AS unitprice,
    CAST(discountpercent AS NUMERIC(5,2)) AS discountpercent,
    TRIM(saleschannel) AS saleschannel,
    TRIM(salesrep) AS salesrep,
    TRIM(customertype) AS customertype,
    CAST(revenue AS NUMERIC(12,2)) AS revenue
FROM bronze_sales_transactions;

CREATE OR REPLACE VIEW silver_inventory_snapshots AS 
SELECT DISTINCT
    CAST(snapshotdate AS DATE) AS snapshotdate,
    TRIM(storename) AS storename,
    REPLACE(sku, ' ', '') AS sku,
    TRIM(productname) AS productname,
    CAST(onhandinventory AS INTEGER) AS onhandinventory,
    CAST(reorderpoint AS INTEGER) AS reorderpoint,
    CAST(safetystock AS INTEGER) AS safetystock,
    CAST(inventoryvalue AS NUMERIC(12,2)) AS inventoryvalue,
    CASE WHEN TRIM(LOWER(isstockout::TEXT)) IN ('true', '1', 'yes') THEN TRUE ELSE FALSE END AS isstockout,
    CASE WHEN TRIM(LOWER(belowsafetystock::TEXT)) IN ('true', '1', 'yes') THEN TRUE ELSE FALSE END AS belowsafetystock,
    CASE WHEN TRIM(LOWER(isoverstock::TEXT)) IN ('true', '1', 'yes') THEN TRUE ELSE FALSE END AS isoverstock,
    CAST(lostsalesunits AS INTEGER) AS lostsalesunits
FROM bronze_inventory_snapshots;

CREATE OR REPLACE VIEW silver_purchase_orders AS 
SELECT DISTINCT
    TRIM(po_id) AS po_id,
    CAST(orderdate AS DATE) AS orderdate,
    TRIM(suppliername) AS suppliername,
    TRIM(suppliercountry) AS suppliercountry,
    TRIM(warehouseid) AS warehouseid,
    REPLACE(sku, ' ', '') AS sku,
    TRIM(productname) AS productname,
    CAST(orderedqty AS INTEGER) AS orderedqty,
    CASE WHEN unitcost::text ~ '^[0-9]+(\.[0-9]+)?$' THEN CAST(unitcost AS NUMERIC(10,2)) ELSE 0.00 END AS unitcost,
    CAST(expecteddeliverydate AS DATE) AS expecteddeliverydate,
    CAST(actualdeliverydate AS DATE) AS actualdeliverydate,
    TRIM(receivingstore) AS receivingstore,
    TRIM(postatus) AS postatus,
    CAST(receivedqty AS INTEGER) AS receivedqty,
    TRIM(deliveryperformance) AS deliveryperformance,
    TRIM(potype) AS potype
FROM bronze_purchase_orders;

CREATE OR REPLACE VIEW silver_returns AS 
SELECT DISTINCT
    TRIM(returnid) AS returnid,
    CAST(returndate AS DATE) AS returndate,
    TRIM(invoiceid) AS invoiceid,
    TRIM(storename) AS storename,
    REPLACE(sku, ' ', '') AS sku,
    TRIM(productname) AS productname,
    TRIM(category) AS category,
    CAST(returnedqty AS INTEGER) AS returnedqty,
    TRIM(returnreason) AS returnreason,
    CAST(refundamount AS NUMERIC(10,2)) AS refundamount
FROM bronze_returns;

CREATE OR REPLACE VIEW silver_promotions AS 
SELECT DISTINCT
    TRIM(promotionid) AS promotionid,
    TRIM(campaignname) AS campaignname,
    REPLACE(sku, ' ', '') AS sku,
    CAST(startdate AS DATE) AS startdate,
    CAST(enddate AS DATE) AS enddate,
    CAST(discountpercent AS NUMERIC(5,2)) AS discountpercent
FROM bronze_promotions;

CREATE OR REPLACE VIEW silver_logistics AS 
SELECT DISTINCT
    TRIM(logisticsid) AS logisticsid,
    TRIM(po_id) AS po_id,
    TRIM(carrier) AS carrier,
    TRIM(shipmentmode) AS shipmentmode,
    CAST(freightcost AS NUMERIC(10,2)) AS freightcost,
    CAST(expecteddelivery AS DATE) AS expecteddelivery,
    CAST(actualdelivery AS DATE) AS actualdelivery,
    TRIM(shipmentstatus) AS shipmentstatus,
    TRIM(origincountry) AS origincountry,
    TRIM(destinationstore) AS destinationstore
FROM bronze_logistics;

CREATE OR REPLACE VIEW silver_warehouse_master AS 
SELECT DISTINCT
    TRIM(warehouseid) AS warehouseid,
    TRIM(warehousename) AS warehousename,
    TRIM(location) AS location,
    CAST(capacitysqft AS INTEGER) AS capacity
FROM bronze_warehouse_master;

-- -----------------------------------------------------------------------------
-- LAYER: GOLD (Dimensional Modeling)
-- -----------------------------------------------------------------------------

-- 1. DIMENSION TABLES
DROP TABLE IF EXISTS dim_products;
CREATE TABLE dim_products AS
SELECT sku, MAX(productname) AS productname, MAX(category) AS category, MAX(subcategory) AS subcategory, 
       MAX(brand) AS brand, MAX(standardcost) AS standardcost, MAX(standardprice) AS standardprice, MAX(status) AS status
FROM silver_product_master 
WHERE sku IS NOT NULL AND sku <> ''
GROUP BY sku;
ALTER TABLE dim_products ADD PRIMARY KEY (sku);

DROP TABLE IF EXISTS dim_stores;
CREATE TABLE dim_stores AS SELECT DISTINCT * FROM silver_store_master WHERE storeid IS NOT NULL AND storeid <> '';
ALTER TABLE dim_stores ADD PRIMARY KEY (storeid);

DROP TABLE IF EXISTS dim_suppliers;
CREATE TABLE dim_suppliers AS SELECT DISTINCT * FROM silver_supplier_master WHERE supplierid IS NOT NULL AND supplierid <> '';
ALTER TABLE dim_suppliers ADD PRIMARY KEY (supplierid);

DROP TABLE IF EXISTS dim_warehouses;
CREATE TABLE dim_warehouses AS SELECT DISTINCT * FROM silver_warehouse_master WHERE warehouseid IS NOT NULL AND warehouseid <> '';
ALTER TABLE dim_warehouses ADD PRIMARY KEY (warehouseid);

-- 2. FACT TABLES
-- Fact Sales
DROP TABLE IF EXISTS fact_sales;
CREATE TABLE fact_sales AS
SELECT s.invoiceid, MIN(s.orderdate) AS orderdate, s.sku, MAX(s.storename) AS storename,
       SUM(s.quantitysold) AS quantitysold, MAX(s.unitprice) AS unitprice, SUM(s.revenue) AS revenue
FROM silver_sales_transactions s
LEFT JOIN dim_products p ON s.sku = p.sku
LEFT JOIN dim_stores st ON s.storename = st.storename
WHERE s.sku IS NOT NULL AND s.sku <> ''
GROUP BY s.invoiceid, s.sku;
ALTER TABLE fact_sales ADD PRIMARY KEY (invoiceid, sku);

-- Fact Inventory
DROP TABLE IF EXISTS fact_inventory;
CREATE TABLE fact_inventory AS
SELECT i.snapshotdate, i.storename, i.sku, 
       SUM(i.onhandinventory) AS onhandinventory, SUM(i.lostsalesunits) AS lostsalesunits,
       SUM(i.inventoryvalue) AS inventoryvalue, MAX(i.reorderpoint) AS reorderpoint
FROM silver_inventory_snapshots i
LEFT JOIN dim_products p ON i.sku = p.sku
LEFT JOIN dim_stores st ON i.storename = st.storename
WHERE i.sku IS NOT NULL AND i.sku <> ''
GROUP BY i.snapshotdate, i.storename, i.sku;
ALTER TABLE fact_inventory ADD PRIMARY KEY (snapshotdate, storename, sku);

-- Fact Purchasing
DROP TABLE IF EXISTS fact_purchasing;
CREATE TABLE fact_purchasing AS
SELECT po.po_id, po.orderdate, po.sku, po.suppliername, po.warehouseid,
       SUM(po.orderedqty) AS orderedqty, SUM(po.receivedqty) AS receivedqty,
       MAX(po.deliveryperformance) AS delivery_performance 
FROM silver_purchase_orders po
LEFT JOIN dim_products p ON po.sku = p.sku
LEFT JOIN dim_suppliers sup ON po.suppliername = sup.suppliername
LEFT JOIN dim_warehouses w ON po.warehouseid = w.warehouseid
WHERE po.sku IS NOT NULL AND po.sku <> ''
GROUP BY po.po_id, po.orderdate, po.sku, po.suppliername, po.warehouseid;
ALTER TABLE fact_purchasing ADD PRIMARY KEY (po_id, sku);

-- -----------------------------------------------------------------------------
-- STAKEHOLDER INSIGHTS
-- -----------------------------------------------------------------------------
 
-- Insight 1: Top 5 Products by Revenue
SELECT p.productname, p.category, SUM(f.revenue) AS total_revenue
FROM fact_sales f
JOIN dim_products p ON f.sku = p.sku
GROUP BY p.productname, p.category
ORDER BY total_revenue DESC LIMIT 5;
 
-- Insight 2: Inventory Stockout Risks
SELECT f.storename, f.sku, f.onhandinventory, f.reorderpoint
FROM fact_inventory f
WHERE f.onhandinventory < f.reorderpoint
ORDER BY f.onhandinventory ASC;
 
-- Insight 3: Supplier Reliability Report
SELECT f.suppliername, COUNT(*) AS total_late_deliveries
FROM fact_purchasing f
WHERE f.delivery_performance = 'Late'
GROUP BY f.suppliername
ORDER BY total_late_deliveries DESC;

-- Insight 4: Month-over-Month Sales Growth

WITH monthly_sales AS (
    -- First, calculate total sales per month
    SELECT
        d.year,
        d.month,
        d.month_name,
        SUM(s.revenue) AS total_sales
    FROM fact_sales s
    JOIN dim_date d ON s.orderdate = d.date
    GROUP BY d.year, d.month, d.month_name
)
SELECT
    year,
    month_name,
    total_sales,
    -- Get the sales value from the previous row
    LAG(total_sales) OVER (ORDER BY year, month) AS prev_month_sales,
    -- Calculate percentage growth: ((Current - Previous) / Previous) * 100
    ROUND(
        ((total_sales - LAG(total_sales) OVER (ORDER BY year, month)) / 
        NULLIF(LAG(total_sales) OVER (ORDER BY year, month), 0)) * 100, 
    2) AS growth_percentage
FROM monthly_sales
ORDER BY year, month;







# Stakeholder Insights

Four business questions answered directly from the Gold layer, each written for a specific
stakeholder rather than as a generic query.

---

### 1. Which products drive the most revenue? *(Merchandising)*
```sql
SELECT p.productname, p.category, SUM(f.revenue) AS total_revenue
FROM fact_sales f
JOIN dim_products p ON f.sku = p.sku
GROUP BY p.productname, p.category
ORDER BY total_revenue DESC LIMIT 5;
```
**Use case:** informs assortment planning and shelf-space allocation — merchandising teams
use this to double down on what's already working.

---

### 2. Which SKUs are at risk of stocking out? *(Procurement)*
```sql
SELECT f.storename, f.sku, f.onhandinventory, f.reorderpoint
FROM fact_inventory f
WHERE f.onhandinventory < f.reorderpoint
ORDER BY f.onhandinventory ASC;
```
**Use case:** triggers reorder alerts before a stockout costs sales. Grain is
snapshot-date × store × SKU, so this can be scheduled to run daily.

---

### 3. Which suppliers deliver late most often? *(Vendor Management)*
```sql
SELECT f.suppliername, COUNT(*) AS total_late_deliveries
FROM fact_purchasing f
WHERE f.delivery_performance = 'Late'
GROUP BY f.suppliername
ORDER BY total_late_deliveries DESC;
```
**Use case:** supports vendor scorecards and contract renegotiation — repeat offenders
surface immediately instead of requiring a manual audit.

---

### 4. Is revenue growing month over month? *(Finance / Leadership)*
```sql
WITH monthly_sales AS (
    SELECT d.year, d.month, d.month_name, SUM(s.revenue) AS total_sales
    FROM fact_sales s
    JOIN dim_date d ON s.orderdate = d.date
    GROUP BY d.year, d.month, d.month_name
)
SELECT year, month_name, total_sales,
       LAG(total_sales) OVER (ORDER BY year, month) AS prev_month_sales,
       ROUND(((total_sales - LAG(total_sales) OVER (ORDER BY year, month))
              / NULLIF(LAG(total_sales) OVER (ORDER BY year, month), 0)) * 100, 2) AS growth_percentage
FROM monthly_sales
ORDER BY year, month;
```
**Use case:** a standing MoM growth trend for leadership reporting, made possible by the
`dim_date` table — no manual date math needed, and the same `dim_date` can be reused against
`fact_inventory` or `fact_purchasing` for any future time-based question.

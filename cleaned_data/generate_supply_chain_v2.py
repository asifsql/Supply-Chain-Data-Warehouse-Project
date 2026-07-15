"""
================================================================================
SUPPLY CHAIN SYNTHETIC DATA GENERATOR  – v2 (Full Portfolio Edition)
================================================================================
Generates 11 CSV files for a complete supply chain analytics portfolio:

  sales_transactions.csv      ~80-90k rows
  purchase_orders.csv         ~9-12k rows
  inventory_snapshots.csv     ~110-130k rows  (bi-weekly, store × SKU)
  returns.csv                 ~1,500-2,500 rows
  promotions.csv              ~120-160 rows
  warehouse_master.csv        5 warehouses
  product_master.csv          163 products
  supplier_master.csv         23 suppliers
  store_master.csv            17 stores
  logistics.csv               freight records attached to POs
  data_quality_report.csv     formal DQ audit

All inventory is CAUSALLY linked to sales and PO receipts.
Stockouts, overstocks, and lost-sales are explicitly tracked.
================================================================================
"""

import os, random, warnings
import numpy as np
import pandas as pd
from datetime import date, timedelta
from faker import Faker

warnings.filterwarnings("ignore")

# ─── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED); np.random.seed(SEED)
fake = Faker(); Faker.seed(SEED)

OUTPUT_DIR = "generated_supply_chain_project_v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SIM_START   = date(2024, 10,  1)
SIM_END     = date(2026, 12, 31)
ALL_DATES   = pd.date_range(SIM_START, SIM_END, freq="D")
N_DAYS      = len(ALL_DATES)

# ─── DQ tracking ──────────────────────────────────────────────────────────────
DQ = dict(
    missing_values=0, duplicates=0, inconsistent_skus=0,
    naming_inconsistencies=0, invalid_dates=0,
    negative_inventory_adjustments=0, total=0,
)
def bump(key, n=1):
    DQ[key] += n; DQ["total"] += n

# ══════════════════════════════════════════════════════════════════════════════
# 1. WAREHOUSE MASTER  (distribution centre layer)
# ══════════════════════════════════════════════════════════════════════════════
def build_warehouse_master():
    rows = [
        ("WH-001","Northeast DC",   "Northeast", "Boston, MA",     85000),
        ("WH-002","Southeast DC",   "Southeast", "Charlotte, NC",  72000),
        ("WH-003","Midwest DC",     "Midwest",   "Columbus, OH",   91000),
        ("WH-004","West DC",        "West",      "Denver, CO",     68000),
        ("WH-005","Central Reserve","Midwest",   "Indianapolis, IN",55000),
    ]
    df = pd.DataFrame(rows, columns=["WarehouseID","WarehouseName","Region",
                                      "Location","CapacitySqFt"])
    df.to_csv(f"{OUTPUT_DIR}/warehouse_master.csv", index=False)
    return df

# ── Region → Warehouse mapping ────────────────────────────────────────────────
REGION_WH = {
    "Northeast": "WH-001",
    "Southeast": "WH-002",
    "Midwest":   "WH-003",
    "West":      "WH-004",
}

# ══════════════════════════════════════════════════════════════════════════════
# 2. STORE MASTER
# ══════════════════════════════════════════════════════════════════════════════
def build_store_master():
    rows = [
        ("STR-001","Boston Flagship",       "Northeast","Boston",        "2021-03-12","Flagship","James Thompson"),
        ("STR-002","Atlanta Flagship",      "Southeast","Atlanta",       "2021-06-05","Flagship","Maria Garcia"),
        ("STR-003","Chicago Flagship",      "Midwest",  "Chicago",       "2021-09-17","Flagship","David Hernandez"),
        ("STR-004","Denver Standard",       "West",     "Denver",        "2022-01-08","Standard","Susan Martinez"),
        ("STR-005","Philadelphia Standard", "Northeast","Philadelphia",  "2022-04-22","Standard","Robert Robinson"),
        ("STR-006","Charlotte Standard",    "Southeast","Charlotte",     "2022-08-14","Standard","Linda Clark"),
        ("STR-007","Columbus Standard",     "Midwest",  "Columbus",      "2024-11-03","Standard","Michael Rodriguez"),
        ("STR-008","Tampa Compact",         "Southeast","Tampa",         "2025-01-19","Compact", "Karen Lewis"),
        ("STR-009","Phoenix Compact",       "West",     "Phoenix",       "2025-02-28","Compact", "William Lee"),
        ("STR-010","Providence Express",    "Northeast","Providence",    "2025-04-07","Express", "Lisa Walker"),
        ("STR-011","Indianapolis Standard", "Midwest",  "Indianapolis",  "2025-05-12","Standard","Richard Hall"),
        ("STR-012","Nashville Compact",     "Southeast","Nashville",     "2025-07-21","Compact", "Barbara Allen"),
        ("STR-013","Salt Lake City Express","West",     "Salt Lake City","2025-09-08","Express", "Joseph Young"),
        ("STR-014","Detroit Compact",       "Midwest",  "Detroit",       "2025-11-17","Compact", "Nancy King"),
        ("STR-015","Raleigh Standard",      "Southeast","Raleigh",       "2026-01-06","Standard","Thomas Wright"),
        ("STR-016","Hartford Express",      "Northeast","Hartford",      "2026-03-14","Express", "Betty Scott"),
        ("STR-017","Milwaukee Compact",     "Midwest",  "Milwaukee",     "2026-06-01","Compact", "Charles Torres"),
    ]
    df = pd.DataFrame(rows, columns=["StoreID","StoreName","Region","City",
                                      "OpeningDate","StoreType","StoreManager"])
    df.to_csv(f"{OUTPUT_DIR}/store_master.csv", index=False)
    return df

# ══════════════════════════════════════════════════════════════════════════════
# 3. SUPPLIER MASTER
# ══════════════════════════════════════════════════════════════════════════════
def build_supplier_master():
    rows = [
        # ID, Name, Country, Lead, Reliability, ContractStart, Terms, Category, TrendType
        ("SUP-001","NexGen Wholesale",      "USA",    4, 0.97,"2021-01-15","Net 30","Grocery",    "stable"),
        ("SUP-002","PrimePack Industries",  "USA",    5, 0.94,"2021-03-22","Net 30","Packaging",  "stable"),
        ("SUP-003","SunCoast Distributors", "USA",    6, 0.91,"2021-06-10","Net 45","Beverages",  "improving"),
        ("SUP-004","Atlantic Foods Co.",    "Canada", 8, 0.88,"2021-09-01","Net 30","Grocery",    "stable"),
        ("SUP-005","Pinnacle Supply Group", "USA",    3, 0.96,"2022-02-14","Net 15","Electronics","stable"),
        ("SUP-006","Meridian Logistics",    "Mexico",10, 0.83,"2022-04-05","Net 45","General",    "declining"),
        ("SUP-007","BlueStar Trading",      "China", 21, 0.78,"2022-07-18","Net 60","General",    "declining"),
        ("SUP-008","EastBridge Imports",    "China", 25, 0.72,"2022-10-30","Net 60","Electronics","seasonal"),
        ("SUP-009","Harvest Fields LLC",    "USA",    5, 0.93,"2022-12-01","Net 30","Perishables","seasonal"),
        ("SUP-010","Cascade Natural Foods", "USA",    4, 0.95,"2023-03-07","Net 30","Organic",    "improving"),
        ("SUP-011","Delta Procurement",     "Canada", 9, 0.85,"2023-05-19","Net 45","General",    "stable"),
        ("SUP-012","Vanguard Supplies",     "USA",    6, 0.90,"2023-08-11","Net 30","Grocery",    "stable"),
        ("SUP-013","TrueNorth Exports",     "Canada",12, 0.80,"2023-11-22","Net 45","Seasonal",   "seasonal"),
        ("SUP-014","Pacific Rim Trading",   "Taiwan",18, 0.76,"2024-01-08","Net 60","Electronics","declining"),
        ("SUP-015","Sterling Wholesale",    "USA",    4, 0.92,"2024-03-15","Net 30","Grocery",    "stable"),
        ("SUP-016","Brightway Products",    "USA",    7, 0.87,"2024-05-20","Net 30","General",    "improving"),
        ("SUP-017","Continental Foods",     "Germany",14,0.86,"2024-07-01","Net 45","Specialty",  "stable"),
        ("SUP-018","Apex Distribution",     "USA",    5, 0.94,"2024-09-10","Net 30","Beverages",  "stable"),
        ("SUP-019","GreenLeaf Organics",    "USA",    3, 0.96,"2024-10-01","Net 15","Organic",    "improving"),
        ("SUP-020","Solaris Trading Co.",   "UAE",   16, 0.74,"2024-11-15","Net 60","Specialty",  "declining"),
        ("SUP-021","Redwood Suppliers",     "USA",    6, 0.89,"2025-01-20","Net 30","General",    "stable"),
        ("SUP-022","Titan Food Brokers",    "USA",    5, 0.91,"2025-04-08","Net 30","Grocery",    "improving"),
        ("SUP-023","OmniSource Global",     "China", 28, 0.69,"2025-07-01","Net 60","General",    "declining"),
    ]
    pub_cols = ["SupplierID","SupplierName","Country","LeadTimeDays","ReliabilityScore",
                "ContractStartDate","PaymentTerms","SupplierCategory"]
    df = pd.DataFrame(rows, columns=pub_cols+["_Trend"])
    df[pub_cols].to_csv(f"{OUTPUT_DIR}/supplier_master.csv", index=False)
    return df  # returns full df including _Trend

# ══════════════════════════════════════════════════════════════════════════════
# 4. PRODUCT MASTER
# ══════════════════════════════════════════════════════════════════════════════
BRANDS = ["SunRise","PureChoice","ValuBrand","NaturePath","ElitePro",
          "FreshFirst","EverGreen","HomeComfort","QuickServe","GoldCrest",
          "BluePeak","ClearSpring","OptimaFood","CoastalSelect","UrbanHarvest"]

# (Category, Subcategory, count, uom_choices, cost_lo, cost_hi, seasonal_profile)
CAT_SPEC = [
    ("Beverages","Carbonated Drinks",  12,["Each","Case/12","Case/24"],0.80, 2.50,"summer"),
    ("Beverages","Juices",             10,["Each","Case/12","Case/24"],1.20, 3.80,"flat"),
    ("Beverages","Water & Sparkling",   8,["Each","Case/24"],          0.60, 1.80,"summer"),
    ("Beverages","Energy Drinks",       7,["Each","Case/24"],          1.50, 4.00,"flat"),
    ("Snacks","Chips & Crisps",        10,["Each","Case/24","Case/48"],0.90, 3.20,"flat"),
    ("Snacks","Nuts & Seeds",           8,["Each","Case/12"],          2.50, 8.00,"holiday"),
    ("Snacks","Cookies & Bars",         9,["Each","Case/24","Case/48"],1.10, 3.50,"holiday"),
    ("Dairy","Cheese",                  8,["Each","Case/12"],          3.50,12.00,"flat"),
    ("Dairy","Yogurt",                  7,["Each","Case/12"],          1.80, 5.00,"flat"),
    ("Dairy","Butter & Spreads",        5,["Each","Case/12"],          2.20, 7.00,"winter"),
    ("Grocery","Canned Goods",         10,["Each","Case/24","Case/6"], 0.80, 3.00,"winter"),
    ("Grocery","Condiments",            8,["Each","Case/12"],          1.50, 6.00,"summer"),
    ("Grocery","Pasta & Grains",        8,["Each","Case/24"],          1.20, 4.50,"flat"),
    ("Frozen Foods","Frozen Meals",     9,["Each","Case/12"],          3.50,11.00,"winter"),
    ("Frozen Foods","Frozen Vegetables",8,["Each","Case/12"],          2.00, 6.00,"flat"),
    ("Frozen Foods","Ice Cream",        6,["Each","Case/12"],          2.50, 7.00,"summer"),
    ("Health & Beauty","Vitamins",      8,["Each","Box/10","Case/24"], 5.00,22.00,"winter"),
    ("Health & Beauty","Personal Care", 7,["Each","Box/10"],           2.50,12.00,"flat"),
    ("Health & Beauty","OTC Medicine",  6,["Each","Box/10"],           3.00,18.00,"winter"),
    ("Household","Cleaning Products",   8,["Each","Case/12","Pack/6"], 1.80, 8.00,"flat"),
    ("Household","Paper Products",      5,["Each","Case/12"],          2.00, 7.00,"flat"),
]

def _sku_variant(s):
    """Return a dirty SKU variant (for DQ injection)."""
    r = random.random()
    if r < 0.25: return s.replace("-","")          # PRD0042
    if r < 0.45: return s.lower()                  # prd-0042
    if r < 0.60: return s.replace("PRD-","P-")     # P-0042
    if r < 0.75: return " "+s                      # leading space
    if r < 0.88: return s+" "                      # trailing space
    return s.replace("PRD-","PRD ")                # space instead of dash

def _name_variant(n):
    """Return a slightly corrupted product/supplier name."""
    r = random.random()
    if r < 0.22: return n.upper()
    if r < 0.44: return n.lower()
    if r < 0.60: return n+" "
    if r < 0.75: return " "+n
    pos = random.randint(1, max(1,len(n)-2))
    return n[:pos]+random.choice("aeiouAEIOU")+n[pos+1:]

def build_product_master(supplier_df):
    sids   = supplier_df["SupplierID"].tolist()
    snames = supplier_df["SupplierName"].tolist()
    adj    = ["Original","Classic","Premium","Value","Select","Deluxe","Lite","Pro","Plus"]
    records= []
    idx    = 1

    for cat,sub,cnt,uoms,clo,chi,seas in CAT_SPEC:
        if idx > 163: break
        for _ in range(cnt):
            if idx > 163: break
            brand  = random.choice(BRANDS)
            cost   = round(random.uniform(clo, chi), 2)
            margin = random.uniform(0.18, 0.60)
            price  = round(cost*(1+margin), 2)
            uom    = random.choice(uoms)
            si     = random.randrange(len(sids))

            # Popularity: beta-distributed → realistic ABC spread
            pop = float(np.random.beta(1.5, 5.0))   # most products slow-moving

            # Growth trajectory for lifecycle effects
            lifecycle = random.choices(
                ["mature","growing","declining","niche","seasonal"],
                weights=[40,20,15,15,10]
            )[0]

            # Launch date: 80% pre-sim, 20% during sim
            if random.random() < 0.80:
                launch = fake.date_between(date(2019,1,1), SIM_START - timedelta(1))
            else:
                launch = fake.date_between(SIM_START+timedelta(30), date(2026,1,1))

            disc_date = None
            if random.random() < 0.092:
                status = "Discontinued"
                disc_date = str(fake.date_between(SIM_START+timedelta(90), SIM_END-timedelta(30)))
            elif date.fromisoformat(str(launch)) > SIM_START:
                status = "New Launch"
            else:
                status = "Active"

            weight = ""
            if cat in ("Snacks","Grocery"):
                weight = f" {random.choice([200,250,300,400,500,750,1000])}g"

            records.append({
                "SKU":               f"PRD-{idx:04d}",
                "ProductName":       f"{brand} {sub} {random.choice(adj)}{weight}",
                "Category":          cat,
                "Subcategory":       sub,
                "Brand":             brand,
                "StandardCost":      cost,
                "StandardPrice":     price,
                "LaunchDate":        str(launch),
                "DiscontinuationDate":disc_date or "",
                "Status":            status,
                "PreferredSupplier": snames[si],
                "UnitOfMeasure":     uom,
                "_SupplierID":       sids[si],
                "_SupplierIdx":      si,
                "_Popularity":       pop,
                "_Seasonality":      seas,
                "_Lifecycle":        lifecycle,
            })
            idx += 1

    df = pd.DataFrame(records)
    pub = ["SKU","ProductName","Category","Subcategory","Brand","StandardCost",
           "StandardPrice","LaunchDate","DiscontinuationDate","Status",
           "PreferredSupplier","UnitOfMeasure"]
    df[pub].to_csv(f"{OUTPUT_DIR}/product_master.csv", index=False)
    return df

# ══════════════════════════════════════════════════════════════════════════════
# 5. PROMOTIONS
# ══════════════════════════════════════════════════════════════════════════════
CAMPAIGNS = [
    "Back to School","Summer Refresh","Fall Harvest","Holiday Blowout",
    "New Year New You","Spring Clean","Super Bowl Special","Memorial Day",
    "Labor Day","Black Friday Preview","Valentine Sale","Easter Basket",
]

def build_promotions(product_df):
    """
    ~130–160 promotions. Each covers 1–3 SKUs for 7–21 days with a discount.
    Returns df + a lookup dict: date → {sku: discount_pct}.
    """
    active_skus = product_df[product_df["Status"]!="Discontinued"]["SKU"].tolist()
    records = []
    promo_lookup = {}   # date_str -> {sku: pct}
    pid = 1

    # One major campaign per month
    sim_months = pd.date_range(SIM_START, SIM_END, freq="MS")
    for m in sim_months:
        n_promos = random.randint(4, 8)
        for _ in range(n_promos):
            start = m + timedelta(days=random.randint(0, 22))
            dur   = random.randint(7, 21)
            end   = start + timedelta(days=dur)
            if end.date() > SIM_END: end = pd.Timestamp(SIM_END)
            skus_in_promo = random.sample(active_skus, random.randint(1,4))
            disc = round(random.choice([0.05,0.08,0.10,0.12,0.15,0.20,0.25]), 2)
            camp = random.choice(CAMPAIGNS)
            for sku in skus_in_promo:
                records.append({
                    "PromotionID":     f"PROMO-{pid:04d}",
                    "CampaignName":    camp,
                    "SKU":             sku,
                    "StartDate":       str(start.date()),
                    "EndDate":         str(end.date()),
                    "DiscountPercent": disc,
                })
                # Populate lookup
                for day_offset in range((end.date()-start.date()).days+1):
                    ds = str((start + timedelta(days=day_offset)).date())
                    promo_lookup.setdefault(ds, {})[sku] = disc
            pid += 1

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/promotions.csv", index=False)
    return df, promo_lookup

# ══════════════════════════════════════════════════════════════════════════════
# 6. SEASONALITY HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def build_demand_multipliers():
    """
    Returns [4 × N_DAYS] array: profiles flat/summer/winter/holiday.
    Rows in order: flat, summer, winter, holiday.
    """
    months = ALL_DATES.month.to_numpy()
    dows   = ALL_DATES.dayofweek.to_numpy()

    weekly = np.where(dows>=5, 1.32, np.where(dows==4, 1.06, 1.00))

    M = {
        "flat":   np.array([0.95,0.90,0.97,1.00,1.02,1.03,1.05,1.04,1.00,0.98,1.02,1.08]),
        "summer": np.array([0.78,0.76,0.88,1.00,1.18,1.35,1.45,1.40,1.22,0.98,0.85,0.80]),
        "winter": np.array([1.28,1.20,1.06,0.90,0.82,0.78,0.76,0.80,0.88,0.98,1.18,1.35]),
        "holiday":np.array([0.82,0.78,0.86,0.90,0.95,1.00,1.05,1.12,1.15,1.22,1.38,1.55]),
    }

    qe   = np.where((np.isin(months,[3,6,9,12]))&(ALL_DATES.day>=25), 1.20, 1.00)
    hol  = np.ones(N_DAYS)
    for i,d in enumerate(ALL_DATES):
        mo,dy = d.month, d.day
        if mo==11 and 22<=dy<=29: hol[i]=1.42
        elif mo==12 and 20<=dy<=26: hol[i]=1.58
        elif mo==7  and dy in(3,4,5): hol[i]=1.28
        elif mo==1  and dy<=3:      hol[i]=1.22
        elif mo==2  and dy in(13,14,15): hol[i]=1.12

    base = weekly * qe * hol
    return {p: base * M[p][months-1] for p in M}

def store_maturity(open_date_str):
    od  = pd.Timestamp(open_date_str)
    raw = np.array((ALL_DATES - od).days, dtype=np.float32)
    mo  = np.clip(raw/30.44, 0, None)
    return np.minimum(1.0, 0.28 + 0.72*(mo/12)).astype(np.float32)

def product_launch_mask(launch_str):
    ld = pd.Timestamp(launch_str)
    return np.array(ALL_DATES >= ld, dtype=bool)

def product_disc_mask(disc_str):
    """Mask True on days BEFORE discontinuation (product still active)."""
    if not disc_str:
        return np.ones(N_DAYS, dtype=bool)
    dd = pd.Timestamp(disc_str)
    return np.array(ALL_DATES < dd, dtype=bool)

def store_open_mask(open_date_str):
    od = pd.Timestamp(open_date_str)
    return np.array(ALL_DATES >= od, dtype=bool)

REG_F = {"Northeast":1.16,"Southeast":1.00,"Midwest":1.06,"West":0.88}

# Regional product preference matrix (category affinity by region)
REG_CAT_AFFINITY = {
    "Northeast": {"Beverages":1.10,"Health & Beauty":1.20,"Grocery":1.05,"Snacks":0.95,"Dairy":1.00,"Frozen Foods":0.95,"Household":1.00},
    "Southeast": {"Beverages":1.15,"Health & Beauty":0.95,"Grocery":1.10,"Snacks":1.08,"Dairy":0.98,"Frozen Foods":1.02,"Household":1.00},
    "Midwest":   {"Beverages":0.95,"Health & Beauty":1.00,"Grocery":1.12,"Snacks":1.05,"Dairy":1.10,"Frozen Foods":1.08,"Household":1.05},
    "West":      {"Beverages":0.98,"Health & Beauty":1.15,"Grocery":0.92,"Snacks":0.95,"Dairy":0.90,"Frozen Foods":0.95,"Household":0.98},
}

# Lifecycle demand modifier per month-in-sim
def lifecycle_factor(lifecycle, month_idx):
    """month_idx = months since SIM_START (0-27)."""
    if lifecycle == "growing":
        return min(1.6, 0.60 + 0.04*month_idx)
    elif lifecycle == "declining":
        return max(0.30, 1.20 - 0.04*month_idx)
    elif lifecycle == "niche":
        return 0.25
    elif lifecycle == "seasonal":
        # peaks at months 6,18 (roughly mid-year)
        return 0.60 + 0.50*abs(math.sin(math.pi*month_idx/12))
    else:   # mature
        return 1.00

import math

# ══════════════════════════════════════════════════════════════════════════════
# 7. SALES TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
CHANNELS    = ["Wholesale","Retail Counter","Online","Phone Order"]
CW          = [38,30,22,10]
CUST_TYPES  = ["Retailer","Restaurant","Institution","Individual","Corporate"]
CTW         = [32,22,20,12,14]
CUST_ORDER_SIZE = {"Retailer":4,"Restaurant":8,"Institution":12,"Individual":1,"Corporate":6}
REPS = ["Jordan Smith","Casey Brown","Morgan Davis","Taylor Wilson","Alex Johnson",
        "Riley Martinez","Quinn Anderson","Avery Thomas","Blake Jackson","Jamie White"]

def build_sales(store_df, product_df, supplier_df, promo_lookup):
    sup_name_map = dict(zip(supplier_df["SupplierID"], supplier_df["SupplierName"]))
    dem_mult     = build_demand_multipliers()

    active = product_df[product_df["Status"]!="Discontinued"].reset_index(drop=True)
    n_prod = len(active)

    months_arr = np.array([(d.year-SIM_START.year)*12+(d.month-SIM_START.month)
                            for d in ALL_DATES], dtype=np.float32)
    price_drift = (1.0 + months_arr * 0.0019).astype(np.float32)

    all_records    = []
    inv_counter    = [1]

    for _, store in store_df.iterrows():
        sname  = store["StoreName"]
        region = store["Region"]
        open_s = store["OpeningDate"]
        rf     = REG_F[region]
        cat_af = REG_CAT_AFFINITY[region]

        open_mask = store_open_mask(open_s)
        mat_arr   = store_maturity(open_s)

        for pi in range(n_prod):
            prod    = active.iloc[pi]
            sku     = prod["SKU"]
            pname   = prod["ProductName"]
            cat     = prod["Category"]
            sup_id  = prod["_SupplierID"]
            sup_nm  = sup_name_map.get(sup_id,"")
            std_p   = float(prod["StandardPrice"])
            pop     = float(prod["_Popularity"])
            seas    = prod["_Seasonality"]
            lc      = prod["_Lifecycle"]

            launch_mask = product_launch_mask(str(prod["LaunchDate"]))
            disc_mask   = product_disc_mask(str(prod.get("DiscontinuationDate","")))

            # Category regional affinity
            cat_mult = cat_af.get(cat, 1.00)

            seas_arr = dem_mult[seas]
            rng = np.random.default_rng(SEED + pi + hash(sname) % 10000)

            active_days = np.where(open_mask & launch_mask & disc_mask)[0]
            if len(active_days)==0: continue

            for di in active_days:
                mo_idx  = int(months_arr[di])
                lc_f    = lifecycle_factor(lc, mo_idx)
                base_r  = pop * 0.270 * mat_arr[di] * rf * cat_mult * seas_arr[di] * lc_f
                if base_r < 0.001: continue

                n_txn = int(rng.poisson(base_r))
                if n_txn == 0: continue

                d = ALL_DATES[di]
                d_str = str(d.date())

                drift   = float(price_drift[di])
                promo_d = promo_lookup.get(d_str,{}).get(sku, 0.0)
                promo_m = 1.0 - promo_d   # price after promo

                cust = random.choices(CUST_TYPES, weights=CTW)[0]
                base_qty = CUST_ORDER_SIZE.get(cust, 2)
                qty  = max(1, int(rng.poisson(max(1, n_txn * base_qty))))

                # Manual discount (stacked or standalone)
                extra_disc = round(random.choice([0.0,0.05,0.10,0.15,0.20]),2) if random.random()<0.12 else 0.0
                total_disc = min(0.50, promo_d + extra_disc)

                up  = round(std_p * drift * promo_m, 2)
                rev = round(qty * up * (1 - extra_disc), 2)

                ch = random.choices(CHANNELS, weights=CW)[0]
                rp = random.choice(REPS)

                all_records.append((
                    f"INV-{inv_counter[0]:07d}",
                    d_str, sname, region, sku, pname, cat,
                    sup_nm, qty, up, round(total_disc,2), ch, rp, cust, rev
                ))
                inv_counter[0] += 1

    cols = ["InvoiceID","OrderDate","StoreName","Region","SKU","ProductName",
            "Category","SupplierName","QuantitySold","UnitPrice","DiscountPercent",
            "SalesChannel","SalesRep","CustomerType","Revenue"]
    df = pd.DataFrame(all_records, columns=cols)
    print(f"  → Raw sales before DQ injection: {len(df):,}")

    # ── DQ injection ──────────────────────────────────────────────────────────
    n = len(df)

    dup_n = int(n*0.0042)
    df = pd.concat([df, df.sample(dup_n, random_state=SEED)], ignore_index=True)
    bump("duplicates", dup_n)

    for col,frac in [("SupplierName",0.011),("SalesRep",0.005)]:
        ix = df.sample(int(n*frac), random_state=SEED+1).index
        df.loc[ix,col] = np.nan
        bump("missing_values", len(ix))

    sku_ix = df.sample(int(n*0.016), random_state=SEED+3).index
    df.loc[sku_ix,"SKU"] = df.loc[sku_ix,"SKU"].apply(_sku_variant)
    bump("inconsistent_skus", len(sku_ix))

    pn_ix = df.sample(int(n*0.010), random_state=SEED+4).index
    df.loc[pn_ix,"ProductName"] = df.loc[pn_ix,"ProductName"].apply(_name_variant)
    bump("naming_inconsistencies", len(pn_ix))

    reg_ix = df.sample(int(n*0.005), random_state=SEED+5).index
    df.loc[reg_ix,"Region"] = df.loc[reg_ix,"Region"].apply(
        lambda x: x.upper() if random.random()<0.5 else x.lower())
    bump("naming_inconsistencies", len(reg_ix))

    out_ix = df.sample(int(n*0.0018), random_state=SEED+6).index
    df.loc[out_ix,"QuantitySold"] = (df.loc[out_ix,"QuantitySold"]*random.randint(10,40)).astype(int)
    bump("total", len(out_ix))

    null_d = df.sample(int(n*0.0030), random_state=SEED+7).index
    df.loc[null_d,"DiscountPercent"] = np.nan
    bump("missing_values", len(null_d))

    sup_vars = {
        "NexGen Wholesale":   ["NexGen Wholesale","Nexgen Wholesale","NEXGEN WHOLESALE","Nex Gen Wholesale"],
        "BlueStar Trading":   ["BlueStar Trading","Blue Star Trading","bluestar trading","BLUESTAR"],
        "Harvest Fields LLC": ["Harvest Fields LLC","Harvest Fields","harvest fields llc","Harvest  Fields"],
        "GreenLeaf Organics": ["GreenLeaf Organics","Green Leaf Organics","greenleaf organics"],
        "SunCoast Distributors":["SunCoast Distributors","Sun Coast Distributors","SUNCOAST DIST."],
    }
    v_ix = df.sample(int(n*0.013), random_state=SEED+8).index
    for i in v_ix:
        cur = df.at[i,"SupplierName"]
        if isinstance(cur,str) and cur in sup_vars:
            df.at[i,"SupplierName"] = random.choice(sup_vars[cur])
    bump("naming_inconsistencies", len(v_ix))

    # Invalid date (bad ERP export – a handful of rows with year typo)
    bad_date_ix = df.sample(int(n*0.0005), random_state=SEED+9).index
    df.loc[bad_date_ix,"OrderDate"] = "2099-01-01"
    bump("invalid_dates", len(bad_date_ix))

    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    df.to_csv(f"{OUTPUT_DIR}/sales_transactions.csv", index=False)
    return df

# ══════════════════════════════════════════════════════════════════════════════
# 8. INVENTORY + PURCHASE ORDERS  (causally linked, full day-by-day sim)
# ══════════════════════════════════════════════════════════════════════════════
CARRIERS     = ["FedEx Freight","UPS Supply Chain","J.B. Hunt","XPO Logistics","Ryder","Echo Global"]
SHIP_MODES   = ["Truck","Air","Rail","Sea"]
MODE_WEIGHTS = [60,15,15,10]

def _supplier_jitter(rel, lead, trend, mo_idx):
    """Compute delivery jitter days based on supplier reliability & trend."""
    # Reliability degrades/improves over time
    if trend == "declining":
        eff_rel = max(0.50, rel - 0.005*mo_idx)
    elif trend == "improving":
        eff_rel = min(0.99, rel + 0.003*mo_idx)
    elif trend == "seasonal":
        # worse in Q4 and Q1
        eff_rel = rel * (0.88 if mo_idx%12 in [2,3,10,11] else 1.00)
    else:
        eff_rel = rel

    if random.random() > eff_rel:               # late
        return random.randint(2, max(2,int(lead*0.7)+3)), "Late"
    elif random.random() > 0.91:                # early
        return -random.randint(1,2), "Early"
    return 0, "OnTime"

def build_inventory_and_pos(store_df, product_df, sales_df, supplier_df, wh_df):
    sup_info = supplier_df.set_index("SupplierID")
    sup_trend_ser = dict(zip(supplier_df["SupplierID"], supplier_df["_Trend"]))

    sup_lead  = dict(zip(supplier_df["SupplierID"], supplier_df["LeadTimeDays"]))
    sup_rel   = dict(zip(supplier_df["SupplierID"], supplier_df["ReliabilityScore"]))
    sup_name  = dict(zip(supplier_df["SupplierID"], supplier_df["SupplierName"]))
    sup_cntry = dict(zip(supplier_df["SupplierID"], supplier_df["Country"]))

    wh_region = dict(zip(wh_df["Region"], wh_df["WarehouseID"]))

    # Aggregate daily sold qty (use canonical SKU lookup)
    sd = sales_df.copy()
    sd["SKU_c"] = sd["SKU"].str.strip().str.upper().str.replace(r"[^A-Z0-9-]","",regex=True)
    daily = (sd.groupby(["OrderDate","StoreName","SKU_c"])["QuantitySold"]
               .sum().reset_index()
               .rename(columns={"SKU_c":"SKU"}))
    daily["OrderDate"] = pd.to_datetime(daily["OrderDate"])
    daily_idx = daily.set_index(["OrderDate","StoreName","SKU"])["QuantitySold"]

    months_arr = np.array(
        [(d.year-SIM_START.year)*12+(d.month-SIM_START.month) for d in ALL_DATES],
        dtype=np.int32
    )

    active   = product_df[product_df["Status"]!="Discontinued"].reset_index(drop=True)
    snap_day = set(i for i,d in enumerate(ALL_DATES)
                   if d.weekday()==6 and (i//7)%2==0)  # bi-weekly Sunday
    snap_day.add(N_DAYS-1)

    snap_records = []
    po_records   = []
    logistics    = []
    po_counter   = [1]
    log_counter  = [1]

    # Stockout tracking (for validation)
    total_stockout_events = [0]
    total_lost_units      = [0]

    for _, store in store_df.iterrows():
        sname  = store["StoreName"]
        open_d = pd.Timestamp(store["OpeningDate"])
        region = store["Region"]
        rf     = REG_F[region]
        wh_id  = wh_region.get(region,"WH-001")

        for _, prod in active.iterrows():
            sku    = prod["SKU"]
            launch = pd.Timestamp(str(prod["LaunchDate"]))
            cost   = float(prod["StandardCost"])
            pop    = float(prod["_Popularity"])
            sup_id = prod["_SupplierID"]
            pname  = prod["ProductName"]
            lc     = prod["_Lifecycle"]

            lead    = sup_lead.get(sup_id, 7)
            rel     = sup_rel.get(sup_id, 0.90)
            trend   = sup_trend_ser.get(sup_id, "stable")

            # Safety stock & reorder point based on avg demand
            avg_dd  = pop * 0.270 * rf * 8 * 1.10   # slight buffer
            ss      = max(2, int(avg_dd * max(3, lead*0.5)))
            rop     = max(6, int(avg_dd * (lead + max(3,lead*0.5))))
            maxs    = max(25, int(rop * random.uniform(2.0, 3.2)))

            on_hand = random.randint(rop, maxs)

            # Pending deliveries list: (delivery_day_idx, qty)
            pending = []
            # Emergency PO flag: avoid triggering too many
            emerg_cooldown = 0

            for di in range(N_DAYS):
                d = ALL_DATES[di]
                if d < open_d or d < launch: continue

                mo_idx = int(months_arr[di])

                # Receive pending POs
                still = []
                for (del_di, qty_r) in pending:
                    if del_di <= di:
                        on_hand += qty_r
                    else:
                        still.append((del_di, qty_r))
                pending = still

                # Deduct daily sales
                try:
                    sold = int(daily_idx.at[(d, sname, sku)])
                except KeyError:
                    sold = 0

                actual_sold = min(sold, max(0, on_hand))
                lost_units  = sold - actual_sold    # demand we couldn't fill
                if lost_units > 0:
                    total_stockout_events[0] += 1
                    total_lost_units[0]      += lost_units

                on_hand = max(0, on_hand - actual_sold)

                # ── Bi-weekly snapshot ────────────────────────────────────────
                if di in snap_day:
                    snap_records.append((
                        str(d.date()), sname, sku, pname,
                        on_hand, rop, ss,
                        round(on_hand*cost, 2),
                        1 if on_hand == 0 else 0,           # IsStockout
                        1 if on_hand < ss else 0,           # BelowSafetyStock
                        1 if on_hand > maxs*0.85 else 0,    # IsOverstock
                        lost_units,
                    ))

                # ── Reorder logic ─────────────────────────────────────────────
                open_qty     = sum(q for (_,q) in pending)
                emerg_cooldown = max(0, emerg_cooldown-1)

                # Regular replenishment
                if on_hand + open_qty < rop:
                    lc_f  = lifecycle_factor(lc, mo_idx)
                    order_q = max(1, int((maxs - on_hand - open_qty) * max(0.6, lc_f)))

                    # Cost: drift + category inflation + supplier shock
                    cost_mult = 1 + mo_idx*0.0022 + random.uniform(-0.015,0.035)
                    if trend=="declining" and random.random()<0.08:
                        cost_mult *= random.uniform(1.05,1.15)   # cost shock
                    uc = round(cost * cost_mult, 4)

                    jit, del_type = _supplier_jitter(rel, lead, trend, mo_idx)
                    exp_di = di + lead
                    act_di = min(exp_di + jit, N_DAYS-1)

                    if random.random() < 0.15:
                        recv_q = max(1, int(order_q*random.uniform(0.55,0.90)))
                        status = "Partial"
                    else:
                        recv_q = order_q
                        status = "Received" if act_di < N_DAYS else "Open"

                    if act_di >= N_DAYS:
                        status = "Open"; recv_q = 0

                    exp_date = str(ALL_DATES[min(exp_di,N_DAYS-1)].date())
                    act_date = str(ALL_DATES[act_di].date()) if status!="Open" else ""

                    raw_sn = sup_name.get(sup_id,"")
                    dirty_sn = raw_sn
                    r2 = random.random()
                    if r2 < 0.04: dirty_sn = raw_sn.upper()
                    elif r2 < 0.07: dirty_sn = raw_sn.lower()

                    ship_mode = random.choices(SHIP_MODES, weights=MODE_WEIGHTS)[0]
                    carrier   = random.choice(CARRIERS)
                    freight   = round(order_q * cost * random.uniform(0.04,0.12), 2)

                    po_id = f"PO-{po_counter[0]:06d}"
                    po_records.append((
                        po_id, str(d.date()), dirty_sn,
                        sup_cntry.get(sup_id,""), wh_id,
                        sku, pname, order_q, uc,
                        exp_date, act_date, sname, status, recv_q,
                        del_type, "Regular"
                    ))
                    logistics.append((
                        f"LOG-{log_counter[0]:06d}",
                        po_id, carrier, ship_mode, freight,
                        exp_date, act_date if act_date else exp_date,
                        "Delivered" if status!="Open" else "In Transit",
                        sup_cntry.get(sup_id,""), sname
                    ))
                    po_counter[0]  += 1
                    log_counter[0] += 1

                    if status != "Open":
                        pending.append((act_di, recv_q))

                # Emergency PO: zero stock + no pending orders + cooldown expired
                elif on_hand == 0 and len(pending)==0 and emerg_cooldown==0 and random.random()<0.60:
                    emerg_q = max(1, int(ss * 2.5))
                    cost_mult = 1 + mo_idx*0.0022 + random.uniform(0.04,0.10)  # premium cost
                    uc = round(cost * cost_mult, 4)
                    # Emergency: air freight → shorter lead (ceil 3 days)
                    emerg_lead = max(2, int(lead*0.35))
                    exp_di = di + emerg_lead
                    act_di = min(exp_di + random.randint(-1,1), N_DAYS-1)
                    exp_date = str(ALL_DATES[min(exp_di,N_DAYS-1)].date())
                    act_date = str(ALL_DATES[act_di].date()) if act_di < N_DAYS else ""

                    raw_sn = sup_name.get(sup_id,"")
                    po_id  = f"PO-{po_counter[0]:06d}"
                    po_records.append((
                        po_id, str(d.date()), raw_sn,
                        sup_cntry.get(sup_id,""), wh_id,
                        sku, pname, emerg_q, uc,
                        exp_date, act_date, sname,
                        "Received" if act_di < N_DAYS else "Open",
                        emerg_q if act_di < N_DAYS else 0,
                        "OnTime", "Emergency"
                    ))
                    logistics.append((
                        f"LOG-{log_counter[0]:06d}",
                        po_id, "FedEx Freight", "Air",
                        round(emerg_q * cost * 0.18, 2),
                        exp_date, act_date if act_date else exp_date,
                        "Delivered" if act_di < N_DAYS else "In Transit",
                        sup_cntry.get(sup_id,""), sname
                    ))
                    po_counter[0]  += 1
                    log_counter[0] += 1

                    if act_di < N_DAYS:
                        pending.append((act_di, emerg_q))
                    emerg_cooldown = 14   # don't re-trigger for 2 weeks

    print(f"  → Stockout events: {total_stockout_events[0]:,}  |  Lost units: {total_lost_units[0]:,}")

    # ── Build DataFrames ───────────────────────────────────────────────────────
    snap_cols = ["SnapshotDate","StoreName","SKU","ProductName",
                 "OnHandInventory","ReorderPoint","SafetyStock","InventoryValue",
                 "IsStockout","BelowSafetyStock","IsOverstock","LostSalesUnits"]
    snap_df   = pd.DataFrame(snap_records, columns=snap_cols)

    po_cols   = ["PO_ID","OrderDate","SupplierName","SupplierCountry","WarehouseID",
                 "SKU","ProductName","OrderedQty","UnitCost",
                 "ExpectedDeliveryDate","ActualDeliveryDate",
                 "ReceivingStore","POStatus","ReceivedQty",
                 "DeliveryPerformance","POType"]
    po_df     = pd.DataFrame(po_records, columns=po_cols)

    log_cols  = ["LogisticsID","PO_ID","Carrier","ShipmentMode","FreightCost",
                 "ExpectedDelivery","ActualDelivery","ShipmentStatus",
                 "OriginCountry","DestinationStore"]
    log_df    = pd.DataFrame(logistics, columns=log_cols)

    # ── DQ: snapshots ─────────────────────────────────────────────────────────
    ns = len(snap_df)
    neg_ix = snap_df.sample(int(ns*0.003), random_state=SEED+10).index
    snap_df.loc[neg_ix,"OnHandInventory"] = -np.random.randint(1,6,size=len(neg_ix))
    bump("negative_inventory_adjustments", len(neg_ix))

    mv_ix = snap_df.sample(int(ns*0.005), random_state=SEED+11).index
    snap_df.loc[mv_ix,"InventoryValue"] = np.nan
    bump("missing_values", len(mv_ix))

    sk_ix = snap_df.sample(int(ns*0.008), random_state=SEED+12).index
    snap_df.loc[sk_ix,"SKU"] = snap_df.loc[sk_ix,"SKU"].apply(_sku_variant)
    bump("inconsistent_skus", len(sk_ix))

    dup_n = int(ns*0.003)
    snap_df = pd.concat([snap_df, snap_df.sample(dup_n, random_state=SEED+13)], ignore_index=True)
    bump("duplicates", dup_n)

    # ── DQ: purchase orders ───────────────────────────────────────────────────
    np_ = len(po_df)
    bd  = po_df.sample(int(np_*0.03), random_state=SEED+14).index
    po_df.loc[bd,"ActualDeliveryDate"] = ""
    bump("missing_values", len(bd))

    ps  = po_df.sample(int(np_*0.012), random_state=SEED+15).index
    po_df.loc[ps,"SKU"] = po_df.loc[ps,"SKU"].apply(_sku_variant)
    bump("inconsistent_skus", len(ps))

    sc  = po_df.sample(int(np_*0.010), random_state=SEED+16).index
    po_df.loc[sc,"SupplierCountry"] = np.nan
    bump("missing_values", len(sc))

    pd_n = int(np_*0.003)
    if pd_n>0:
        po_df = pd.concat([po_df, po_df.sample(pd_n, random_state=SEED+17)], ignore_index=True)
        bump("duplicates", pd_n)

    # ── Emergency POs: post-hoc from stockout snapshots ─────────────────────
    stockout_snaps = snap_df[(snap_df["IsStockout"]==1) &
                              snap_df["SKU"].str.match(r"^PRD-\d{4}$", na=False)].copy()
    sku_sup  = dict(zip(product_df["SKU"], product_df["_SupplierID"]))
    sku_cost = dict(zip(product_df["SKU"], product_df["StandardCost"]))
    sku_nm   = dict(zip(product_df["SKU"], product_df["ProductName"]))
    store_reg= dict(zip(store_df["StoreName"], store_df["Region"]))

    emerg_pos, emerg_logs = [], []
    poe = po_counter[0]; lge = log_counter[0]
    for _, row in stockout_snaps.sample(frac=0.50, random_state=SEED+50).iterrows():
        try:
            snap_dt = pd.Timestamp(row["SnapshotDate"])
        except:
            continue
        order_d = snap_dt + pd.Timedelta(days=random.randint(0,2))
        if order_d.date() > SIM_END: continue
        sku    = row["SKU"]
        sname  = row["StoreName"]
        sid    = sku_sup.get(sku); 
        if not sid: continue
        cost   = sku_cost.get(sku, 2.0)
        pname  = sku_nm.get(sku, "")
        region = store_reg.get(sname,"Northeast")
        wh_id  = wh_region.get(region,"WH-001")
        mo_idx = max(0,(order_d.year-SIM_START.year)*12+(order_d.month-SIM_START.month))
        lead   = sup_lead.get(sid,7)
        uc     = round(cost*(1+mo_idx*0.0022+random.uniform(0.05,0.12)),4)
        elead  = max(2,int(lead*0.35))
        exp_d  = order_d + pd.Timedelta(days=elead)
        act_d  = exp_d  + pd.Timedelta(days=random.randint(-1,1))
        if act_d.date() > SIM_END:
            status="Open"; recv=0; act_str=""
        else:
            status="Received"; recv=max(5,int(row["ReorderPoint"]*1.5)); act_str=str(act_d.date())
        oq    = recv if recv>0 else max(5,int(row["ReorderPoint"]*1.5))
        po_id = f"PO-E{poe:05d}"
        raw_sn= sup_name.get(sid,"")
        emerg_pos.append((po_id,str(order_d.date()),raw_sn,
                          sup_cntry.get(sid,""),wh_id,sku,pname,oq,uc,
                          str(exp_d.date()),act_str,sname,status,recv,"OnTime","Emergency"))
        emerg_logs.append((f"LOG-E{lge:05d}",po_id,"FedEx Freight","Air",
                           round(oq*cost*0.18,2),str(exp_d.date()),
                           act_str if act_str else str(exp_d.date()),
                           "Delivered" if status!="Open" else "In Transit",
                           sup_cntry.get(sid,""),sname))
        poe+=1; lge+=1

    if emerg_pos:
        epo_df  = pd.DataFrame(emerg_pos,  columns=po_df.columns)
        elog_df = pd.DataFrame(emerg_logs, columns=log_df.columns)
        po_df   = pd.concat([po_df,  epo_df],  ignore_index=True)
        log_df  = pd.concat([log_df, elog_df], ignore_index=True)
        print(f"  \u2192 Emergency POs generated: {len(emerg_pos):,}")

    snap_df.to_csv(f"{OUTPUT_DIR}/inventory_snapshots.csv", index=False)
    po_df.to_csv(f"{OUTPUT_DIR}/purchase_orders.csv", index=False)
    log_df.to_csv(f"{OUTPUT_DIR}/logistics.csv", index=False)
    return snap_df, po_df, log_df

# ══════════════════════════════════════════════════════════════════════════════
# 9. RETURNS
# ══════════════════════════════════════════════════════════════════════════════
RETURN_REASONS = ["Damaged","Expired","Customer Return","Incorrect Shipment","Quality Issue"]
RR_WEIGHTS     = [25,20,30,10,15]

def build_returns(sales_df):
    """~1.5-2.5% of transactions generate a return."""
    # Use only valid-date clean transactions
    clean = sales_df[sales_df["OrderDate"] != "2099-01-01"].copy()
    sample_n = int(len(clean)*0.019)
    sampled  = clean.sample(sample_n, random_state=SEED+20)

    records = []
    for rid,(_, row) in enumerate(sampled.iterrows(), 1):
        ret_delay = random.randint(1, 21)
        try:
            orig_date = date.fromisoformat(row["OrderDate"])
            ret_date  = orig_date + timedelta(days=ret_delay)
            if ret_date > SIM_END: ret_date = SIM_END
        except:
            ret_date = SIM_END

        ret_qty = max(1, int(row["QuantitySold"] * random.uniform(0.15, 0.80)))
        reason  = random.choices(RETURN_REASONS, weights=RR_WEIGHTS)[0]

        records.append({
            "ReturnID":      f"RET-{rid:06d}",
            "ReturnDate":    str(ret_date),
            "InvoiceID":     row["InvoiceID"],
            "StoreName":     row["StoreName"],
            "SKU":           row["SKU"],
            "ProductName":   row["ProductName"],
            "Category":      row.get("Category",""),
            "ReturnedQty":   ret_qty,
            "ReturnReason":  reason,
            "RefundAmount":  round(ret_qty * float(row["UnitPrice"]) * random.uniform(0.85,1.00), 2),
        })

    df = pd.DataFrame(records)

    # DQ: a few missing return reasons
    mv_ix = df.sample(int(len(df)*0.012), random_state=SEED+21).index
    df.loc[mv_ix,"ReturnReason"] = np.nan
    bump("missing_values", len(mv_ix))

    df.to_csv(f"{OUTPUT_DIR}/returns.csv", index=False)
    return df

# ══════════════════════════════════════════════════════════════════════════════
# 10. DATA QUALITY REPORT
# ══════════════════════════════════════════════════════════════════════════════
def build_dq_report(sales_df, po_df, snap_df, ret_df, prod_df, sup_df):
    """Formal DQ audit CSV."""

    def count_missing(df, col):
        return int(df[col].isna().sum()) if col in df.columns else 0

    def count_dirty_sku(df, col="SKU"):
        if col not in df.columns: return 0
        return int((~df[col].str.match(r"^PRD-\d{4}$", na=False)).sum())

    rows = [
        # (File, Column, IssueType, Count, Notes)
        ("sales_transactions","SKU","Inconsistent Format",
         count_dirty_sku(sales_df), "Variants: prd-0001, PRD0001, P-0001"),
        ("sales_transactions","SupplierName","Missing Value",
         count_missing(sales_df,"SupplierName"), "Blank ERP export field"),
        ("sales_transactions","SalesRep","Missing Value",
         count_missing(sales_df,"SalesRep"), "Unassigned transactions"),
        ("sales_transactions","DiscountPercent","Missing Value",
         count_missing(sales_df,"DiscountPercent"), "NULL discount cell"),
        ("sales_transactions","OrderDate","Invalid Date",
         int((sales_df["OrderDate"]=="2099-01-01").sum()), "ERP date parsing error"),
        ("sales_transactions","SupplierName","Naming Inconsistency",
         int(sales_df["SupplierName"].dropna().str.contains(r"(?i)nexgen|bluestar|harvest|greenleaf|suncoast",na=False).sum()),
         "Mixed case / spacing variants"),
        ("sales_transactions","Region","Naming Inconsistency",
         int((~sales_df["Region"].dropna().isin(["Northeast","Southeast","Midwest","West"])).sum()),
         "Mixed case: NORTHEAST, northeast"),
        ("sales_transactions","(all)","Duplicate Rows",
         int(sales_df.duplicated().sum()), "ERP export duplicates"),

        ("purchase_orders","SKU","Inconsistent Format",
         count_dirty_sku(po_df), "Variants in PO lines"),
        ("purchase_orders","ActualDeliveryDate","Missing Value",
         int((po_df["ActualDeliveryDate"].fillna("")=="").sum()), "Open POs + blank field artifact"),
        ("purchase_orders","SupplierCountry","Missing Value",
         count_missing(po_df,"SupplierCountry"), "Blank country field"),
        ("purchase_orders","(all)","Duplicate Rows",
         int(po_df.duplicated().sum()), "ERP export duplicates"),

        ("inventory_snapshots","SKU","Inconsistent Format",
         count_dirty_sku(snap_df), "Propagated from ERP"),
        ("inventory_snapshots","InventoryValue","Missing Value",
         count_missing(snap_df,"InventoryValue"), "NULL value cell"),
        ("inventory_snapshots","OnHandInventory","Negative Adjustment",
         int((snap_df["OnHandInventory"]<0).sum()), "ERP correction entries"),
        ("inventory_snapshots","(all)","Duplicate Rows",
         int(snap_df.duplicated().sum()), "ERP export duplicates"),

        ("returns","ReturnReason","Missing Value",
         count_missing(ret_df,"ReturnReason"), "Unclassified returns"),

        ("product_master","(all)","Total Products", len(prod_df), ""),
        ("product_master","Status","Discontinued", int((prod_df["Status"]=="Discontinued").sum()), ""),
        ("product_master","Status","New Launch",    int((prod_df["Status"]=="New Launch").sum()), ""),

        ("supplier_master","(all)","Total Suppliers", len(sup_df), ""),
    ]
    dq_df = pd.DataFrame(rows, columns=["File","Column","IssueType","Count","Notes"])
    dq_df["GeneratedDate"] = str(date.today())
    dq_df.to_csv(f"{OUTPUT_DIR}/data_quality_report.csv", index=False)

    # Summary
    total_issues = (dq_df[dq_df["IssueType"].isin(
        ["Inconsistent Format","Missing Value","Invalid Date",
         "Naming Inconsistency","Duplicate Rows","Negative Adjustment"]
    )]["Count"].sum())
    return dq_df, int(total_issues)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print("="*68)
    print("  SUPPLY CHAIN SYNTHETIC DATA GENERATOR  v2  (Full Portfolio)")
    print(f"  {SIM_START} → {SIM_END}")
    print("="*68)

    print("\n[1/9] Warehouse master …")
    wh_df  = build_warehouse_master()
    print(f"      {len(wh_df)} warehouses")

    print("\n[2/9] Store master …")
    store_df = build_store_master()
    print(f"      {len(store_df)} stores")

    print("\n[3/9] Supplier master …")
    supplier_df = build_supplier_master()
    print(f"      {len(supplier_df)} suppliers  (trends: stable/improving/declining/seasonal)")

    print("\n[4/9] Product master …")
    product_df = build_product_master(supplier_df)
    print(f"      {len(product_df)} products  |  Active: {(product_df.Status=='Active').sum()}  New Launch: {(product_df.Status=='New Launch').sum()}  Discontinued: {(product_df.Status=='Discontinued').sum()}")

    print("\n[5/9] Promotions …")
    promo_df, promo_lookup = build_promotions(product_df)
    print(f"      {len(promo_df)} promotion lines  |  {promo_df['PromotionID'].nunique()} campaigns")

    print("\n[6/9] Sales transactions …")
    sales_df = build_sales(store_df, product_df, supplier_df, promo_lookup)
    print(f"      {len(sales_df):,} rows")

    print("\n[7/9] Inventory snapshots + Purchase orders + Logistics …")
    snap_df, po_df, log_df = build_inventory_and_pos(
        store_df, product_df, sales_df, supplier_df, wh_df)
    print(f"      {len(snap_df):,} snapshot rows")
    print(f"      {len(po_df):,} PO rows  |  Emergency POs: {int((po_df.get('POType','Regular')=='Emergency').sum())}")
    print(f"      {len(log_df):,} logistics records")

    print("\n[8/9] Returns …")
    ret_df = build_returns(sales_df)
    print(f"      {len(ret_df):,} return records  ({len(ret_df)/len(sales_df)*100:.2f}% return rate)")

    print("\n[9/9] Data quality report …")
    dq_df, total_issues = build_dq_report(sales_df, po_df, snap_df, ret_df, product_df, supplier_df)
    print(f"      {total_issues:,} total tracked DQ issues across all files")

    # ── Final validation report ────────────────────────────────────────────────
    print("\n"+"="*68)
    print("  FINAL VALIDATION REPORT")
    print("="*68)
    print(f"  Sales transactions       : {len(sales_df):>12,}")
    print(f"  Purchase orders          : {len(po_df):>12,}")
    print(f"  Inventory snapshots      : {len(snap_df):>12,}")
    print(f"  Returns                  : {len(ret_df):>12,}")
    print(f"  Promotions               : {len(promo_df):>12,}")
    print(f"  Logistics records        : {len(log_df):>12,}")
    print(f"  Products                 : {len(product_df):>12,}")
    print(f"  Suppliers                : {len(supplier_df):>12,}")
    print(f"  Stores                   : {len(store_df):>12,}")
    print(f"  Warehouses               : {len(wh_df):>12,}")
    print(f"  Date range               : {SIM_START} → {SIM_END}")
    print()
    print("  SNAPSHOT METHODOLOGY")
    print("  Bi-weekly Sunday snapshots per active store × SKU combination.")
    print(f"  17 stores × 148 active products × ~59 bi-weekly periods ≈ ~149k max")
    print(f"  Actual: {len(snap_df):,} (reduced by store opening dates & product launches)")
    print()
    print("  INVENTORY LINKAGE")
    stockouts = int(snap_df["IsStockout"].sum()) if "IsStockout" in snap_df else "N/A"
    overstocks= int(snap_df["IsOverstock"].sum()) if "IsOverstock" in snap_df else "N/A"
    below_ss  = int(snap_df["BelowSafetyStock"].sum()) if "BelowSafetyStock" in snap_df else "N/A"
    print(f"  Stockout snapshots       : {stockouts:>12,}")
    print(f"  Below safety stock       : {below_ss:>12,}")
    print(f"  Overstock snapshots      : {overstocks:>12,}")
    emerg = int((po_df["POType"]=="Emergency").sum()) if "POType" in po_df.columns else "N/A"
    late  = int((po_df.get("DeliveryPerformance","")=="Late").sum()) if "DeliveryPerformance" in po_df.columns else "N/A"
    partial= int((po_df["POStatus"]=="Partial").sum())
    print(f"  Emergency POs            : {emerg:>12,}")
    print(f"  Late deliveries          : {late:>12,}")
    print(f"  Partial deliveries       : {partial:>12,}")
    print()
    print("  DQ ISSUES INJECTED")
    print(f"  Duplicate rows           : {DQ['duplicates']:>12,}")
    print(f"  Missing values           : {DQ['missing_values']:>12,}")
    print(f"  Inconsistent SKUs        : {DQ['inconsistent_skus']:>12,}")
    print(f"  Naming inconsistencies   : {DQ['naming_inconsistencies']:>12,}")
    print(f"  Invalid dates            : {DQ['invalid_dates']:>12,}")
    print(f"  Negative inv. adjustments: {DQ['negative_inventory_adjustments']:>12,}")
    print(f"  TOTAL DQ issues          : {DQ['total']:>12,}")
    print()
    print(f"  Output folder: ./{OUTPUT_DIR}/")
    print("="*68)

    files = [
        "sales_transactions.csv","purchase_orders.csv","inventory_snapshots.csv",
        "returns.csv","promotions.csv","logistics.csv","warehouse_master.csv",
        "product_master.csv","supplier_master.csv","store_master.csv",
        "data_quality_report.csv",
    ]
    print("\n  FILES GENERATED:")
    for f in files:
        fp = f"{OUTPUT_DIR}/{f}"
        sz = os.path.getsize(fp)/1024
        print(f"    {f:<40} {sz:>8.1f} KB")

if __name__ == "__main__":
    main()

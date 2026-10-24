
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Project folders
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_DIR / "data" / "customer_loyalty.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"

CHART_DIR.mkdir(parents=True, exist_ok=True)

# Set chart style
sns.set_theme(style="whitegrid")

# Load dataset
df = pd.read_csv(DATA_FILE, parse_dates=["Purchase_Date"])

print("=" * 55)
print("CUSTOMER LOYALTY PROGRAM - DATA ANALYSIS")
print("=" * 55)

# 1. Dataset overview
print("\n1. DATASET OVERVIEW")
print("-" * 40)
print("Total transactions:", len(df))
print("Unique customers:", df["Customer_ID"].nunique())
print("Total columns:", len(df.columns))

print("\nColumn names:")
print(df.columns.tolist())

# 2. Data quality checks
print("\n2. DATA QUALITY CHECK")
print("-" * 40)
print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate transactions:", df["Transaction_ID"].duplicated().sum())

# Remove duplicate transaction records
df = df.drop_duplicates(subset=["Transaction_ID"]).copy()

# 3. Business KPIs
total_customers = df["Customer_ID"].nunique()
total_transactions = df["Transaction_ID"].nunique()
total_revenue = df["Order_Amount"].sum()
total_discount = df["Discount_Amount"].sum()
total_rewards = df["Reward_Cost"].sum()
total_gross_profit = df["Gross_Profit"].sum()
average_order_value = df["Order_Amount"].mean()

repeat_customer_count = (
    df.groupby("Customer_ID")["Transaction_ID"].nunique().gt(1).sum()
)

repeat_purchase_rate = (
    repeat_customer_count / total_customers * 100
    if total_customers else 0
)

print("\n3. KEY PERFORMANCE INDICATORS")
print("-" * 40)
print(f"Unique customers: {total_customers:,}")
print(f"Total transactions: {total_transactions:,}")
print(f"Total revenue: ₹{total_revenue:,.2f}")
print(f"Gross profit before loyalty costs: ₹{total_gross_profit:,.2f}")
print(f"Total discounts: ₹{total_discount:,.2f}")
print(f"Total reward costs: ₹{total_rewards:,.2f}")
print(f"Average order value: ₹{average_order_value:,.2f}")
print(f"Repeat customers: {repeat_customer_count:,}")
print(f"Repeat customer rate: {repeat_purchase_rate:.2f}%")

# 4. Loyalty tier analysis
tier_analysis = df.groupby("Loyalty_Tier").agg(
    Customers=("Customer_ID", "nunique"),
    Transactions=("Transaction_ID", "nunique"),
    Revenue=("Order_Amount", "sum"),
    Gross_Profit=("Gross_Profit", "sum"),
    Discounts=("Discount_Amount", "sum"),
    Reward_Cost=("Reward_Cost", "sum")
).reset_index()

tier_analysis["Average_Order_Value"] = (
    tier_analysis["Revenue"] / tier_analysis["Transactions"]
)

print("\n4. LOYALTY TIER ANALYSIS")
print("-" * 40)
print(tier_analysis.round(2).to_string(index=False))

tier_analysis.to_csv(
    OUTPUT_DIR / "loyalty_tier_analysis.csv",
    index=False
)

# 5. Monthly revenue analysis
df["Month"] = df["Purchase_Date"].dt.to_period("M").astype(str)

monthly_analysis = df.groupby("Month").agg(
    Revenue=("Order_Amount", "sum"),
    Transactions=("Transaction_ID", "nunique"),
    Gross_Profit=("Gross_Profit", "sum")
).reset_index()

print("\n5. MONTHLY REVENUE")
print("-" * 40)
print(monthly_analysis.to_string(index=False))

monthly_analysis.to_csv(
    OUTPUT_DIR / "monthly_revenue_analysis.csv",
    index=False
)

# 6. Prepare financial metrics
df["Net_Contribution_Before_Fixed_Costs"] = (
    df["Gross_Profit"]
    - df["Discount_Amount"]
    - df["Reward_Cost"]
)

net_contribution = df["Net_Contribution_Before_Fixed_Costs"].sum()

print("\n6. CONTRIBUTION AFTER DISCOUNTS AND REWARDS")
print("-" * 40)
print(f"Gross profit: ₹{total_gross_profit:,.2f}")
print(f"Discount costs: ₹{total_discount:,.2f}")
print(f"Reward costs: ₹{total_rewards:,.2f}")
print(f"Contribution after these costs: ₹{net_contribution:,.2f}")

print(
    "\nNote: This is not yet a true loyalty program ROI. "
    "We need a baseline or control group to estimate incremental profit."
)

# 7. Chart 1: Revenue by loyalty tier
plt.figure(figsize=(9, 5))
sns.barplot(
    data=tier_analysis,
    x="Loyalty_Tier",
    y="Revenue",
    hue="Loyalty_Tier",
    legend=False
)
plt.title("Revenue by Loyalty Tier")
plt.xlabel("Loyalty Tier")
plt.ylabel("Revenue (₹)")
plt.tight_layout()
plt.savefig(CHART_DIR / "revenue_by_tier.png", dpi=300)
plt.close()

# 8. Chart 2: Monthly revenue
plt.figure(figsize=(11, 5))
sns.lineplot(
    data=monthly_analysis,
    x="Month",
    y="Revenue",
    marker="o"
)
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue (₹)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(CHART_DIR / "monthly_revenue.png", dpi=300)
plt.close()

# 9. Chart 3: Loyalty tier customer distribution
customer_tiers = df[
    ["Customer_ID", "Loyalty_Tier"]
].drop_duplicates("Customer_ID")

tier_counts = customer_tiers["Loyalty_Tier"].value_counts()

plt.figure(figsize=(7, 7))
plt.pie(
    tier_counts.values,
    labels=tier_counts.index,
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Customer Distribution by Loyalty Tier")
plt.tight_layout()
plt.savefig(CHART_DIR / "customer_distribution.png", dpi=300)
plt.close()

# 10. Chart 4: Program costs versus gross profit
cost_comparison = pd.DataFrame({
    "Metric": ["Gross Profit", "Discount Costs", "Reward Costs"],
    "Amount": [total_gross_profit, total_discount, total_rewards]
})

plt.figure(figsize=(9, 5))
sns.barplot(
    data=cost_comparison,
    x="Metric",
    y="Amount",
    hue="Metric",
    legend=False
)
plt.title("Gross Profit vs Loyalty Costs")
plt.xlabel("")
plt.ylabel("Amount (₹)")
plt.tight_layout()
plt.savefig(CHART_DIR / "profit_and_costs.png", dpi=300)
plt.close()

# Save cleaned transaction dataset for Power BI
df.to_csv(
    OUTPUT_DIR / "cleaned_customer_loyalty.csv",
    index=False
)

print("\n7. CHARTS CREATED")
print("-" * 40)

for chart in sorted(CHART_DIR.glob("*.png")):
    print(chart.name)

print("\nAnalysis completed successfully!")
print("Charts folder:", CHART_DIR)
print("Output folder:", OUTPUT_DIR)

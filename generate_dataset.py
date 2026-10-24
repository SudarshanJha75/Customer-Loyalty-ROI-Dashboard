
import pandas as pd
import numpy as np
from pathlib import Path

# Make results reproducible
np.random.seed(42)

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Dataset settings
number_of_customers = 1000
number_of_transactions = 5000

# Customer information
customer_ids = [
    f"CUST{i:04d}"
    for i in range(1, number_of_customers + 1)
]

loyalty_tiers = ["Bronze", "Silver", "Gold", "Platinum"]
tier_probabilities = [0.40, 0.30, 0.20, 0.10]

customer_data = pd.DataFrame({
    "Customer_ID": customer_ids,
    "Loyalty_Tier": np.random.choice(
        loyalty_tiers,
        size=number_of_customers,
        p=tier_probabilities
    ),
    "Customer_Segment": np.random.choice(
        ["Regular", "Premium", "Occasional"],
        size=number_of_customers,
        p=[0.50, 0.25, 0.25]
    ),
    "Join_Date": pd.to_datetime(
        np.random.choice(
            pd.date_range("2024-01-01", "2025-12-31"),
            size=number_of_customers
        )
    )
})

# Select customers for transactions
transaction_customers = np.random.choice(
    customer_ids,
    size=number_of_transactions
)

transactions = pd.DataFrame({
    "Transaction_ID": [
        f"TXN{i:05d}"
        for i in range(1, number_of_transactions + 1)
    ],
    "Customer_ID": transaction_customers,
    "Purchase_Date": pd.to_datetime(
        np.random.choice(
            pd.date_range("2025-01-01", "2025-12-31"),
            size=number_of_transactions
        )
    ),
    "Order_Amount": np.random.gamma(
        shape=4,
        scale=500,
        size=number_of_transactions
    ).round(2)
})

# Add customer attributes to each transaction
transactions = transactions.merge(
    customer_data,
    on="Customer_ID",
    how="left"
)

# Calculate discounts and rewards
transactions["Discount_Amount"] = (
    transactions["Order_Amount"]
    * np.random.uniform(0.01, 0.10, number_of_transactions)
).round(2)

transactions["Reward_Cost"] = (
    transactions["Order_Amount"]
    * np.random.uniform(0.01, 0.05, number_of_transactions)
).round(2)

# Example transaction-level gross margin assumption
transactions["Gross_Margin_Rate"] = np.random.uniform(
    0.20, 0.45, number_of_transactions
).round(3)

transactions["Gross_Profit"] = (
    transactions["Order_Amount"]
    * transactions["Gross_Margin_Rate"]
).round(2)

# Count purchases for each customer
purchase_counts = transactions.groupby("Customer_ID")[
    "Transaction_ID"
].transform("count")

transactions["Is_Repeat_Customer"] = (
    purchase_counts > 1
).astype(int)

# Save customer master data separately
customer_data.to_csv(
    DATA_DIR / "customers.csv",
    index=False
)

# Save transaction data
transactions.to_csv(
    DATA_DIR / "customer_loyalty.csv",
    index=False
)

print("Dataset generated successfully!")
print(f"Customers: {len(customer_data)}")
print(f"Transactions: {len(transactions)}")
print(f"Files saved in: {DATA_DIR}")

print("\nSample transactions:")
print(transactions.head())

print("\nLoyalty tier distribution:")
print(transactions["Loyalty_Tier"].value_counts())
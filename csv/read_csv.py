import dask.dataframe as dd
import pandas as pd

from decimal import Decimal

# Read the CSV file
df = dd.read_csv('csv/input_csvs/zouk_point.csv')

# Compute the dataframe to bring it into memory
# Note: Be careful with large datasets as this might exhaust your memory
df_computed = df.compute()

empty_email = []
customer_without_email = 0

zero_balance = []
customer_with_zero_balance = 0

total_customers = 0

result = []
# Iterate over the rows
for index, row in df_computed.iterrows():
    row = dict(row)
    email = row.get('Email',"")
    amount = str(row.get('Points Balance'))
    amount = Decimal(amount.replace(',', ''))
    if (pd.isna(email) or not email) and amount:
        empty_email.append(index+2)
        customer_without_email+=1
        continue
    
    if not amount:
        zero_balance.append(index+2)
        customer_with_zero_balance+=1
    
    total_customers+=1

print(f"total_customers==>{total_customers}")
print(f"customers_without_email==>{customer_without_email}")
print(f"customers_with_zero_balance==>{customer_with_zero_balance}")


   
    



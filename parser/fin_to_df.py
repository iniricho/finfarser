# parser/fin_to_df.py

import pandas as pd

def transactions_to_dataframe(statements):
    """
    Given a list of mt940.Statement objects, flatten them into one DataFrame.
    """
    rows = []
    for stmt in statements:
        account_id = stmt.account_id
        opening_balance = stmt.data.get('opening_balance')
        closing_balance = stmt.data.get('closing_balance')
        for txn in stmt.transactions:
            # txn is an mt940.models.Transaction object
            rows.append({
                'account_id': account_id,
                'statement_number': stmt.number,
                'date': txn.data.get('date'),
                'entry_date': txn.data.get('entry_date'),
                'amount': txn.data.get('amount'),
                'dc_mark': txn.data.get('debit_credit_mark'),
                'transaction_type': txn.data.get('transaction_type'),
                'customer_reference': txn.data.get('customer_reference'),
                'bank_reference': txn.data.get('bank_reference'),
                'description': txn.data.get('transaction_details'),
            })

    df = pd.DataFrame(rows)
    # Convert dates to datetime
    df['date'] = pd.to_datetime(df['date'])
    df['entry_date'] = pd.to_datetime(df['entry_date'], errors='coerce')
    # Normalize amount: ensure numeric, use absolute value, adjust sign by D/C mark
    def normalize_amount(row):
        amt = float(row['amount'])
        if row['dc_mark'] == 'D':
            return -abs(amt)
        return abs(amt)

    df['amount'] = df.apply(normalize_amount, axis=1)
    return df

def clean_dataframe(df):
    """
    Perform any further cleaning: e.g., fill missing references, trim whitespace.
    """
    # Drop duplicate rows (if any)
    df = df.drop_duplicates()
    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include='object').columns
    for col in str_cols:
        df[col] = df[col].str.strip()
    return df

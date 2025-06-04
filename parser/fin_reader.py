# parser/fin_reader.py

import mt940

def parse_fin_file(filepath):
    """
    Reads a .fin (MT940) file and returns a list of Statement objects.
    Each Statement contains:
      - statement.number, statement.account_id
      - statement.opening_balance, statement.closing_balance
      - statement.transactions (list of Transaction objects)
    """
    with open(filepath, 'rb') as f:
        raw_data = f.read()
    # The mt940 library automatically splits multiple messages if present
    transactions = mt940.parse(raw_data)
    return transactions

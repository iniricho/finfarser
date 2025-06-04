# cli.py

import argparse
import sys
import os
from parser.fin_reader import parse_fin_file
from parser.fin_to_df import transactions_to_dataframe, clean_dataframe

def main():
    parser = argparse.ArgumentParser(
        description="Parse SWIFT .fin files into CSV, JSON, or SQLite."
    )
    parser.add_argument(
        'inputs',
        metavar='FILE',
        nargs='+',
        help='One or more .fin files (MT940) to process.'
    )
    parser.add_argument(
        '-o', '--output',
        metavar='OUTPUT',
        help='Output path (file or directory). Defaults to current directory.',
        default='.'
    )
    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'sqlite'],
        default='csv',
        help='Desired output format.'
    )
    parser.add_argument(
        '--sqlite-db',
        metavar='DB_PATH',
        help='If format=sqlite, path to SQLite database file.'
    )

    args = parser.parse_args()

    all_dfs = []
    for infile in args.inputs:
        if not os.path.isfile(infile):
            print(f"Error: {infile} not found.", file=sys.stderr)
            continue
        try:
            stmts = parse_fin_file(infile)
            df = transactions_to_dataframe(stmts)
            df = clean_dataframe(df)
            all_dfs.append(df)
        except Exception as e:
            print(f"Failed to parse {infile}: {e}", file=sys.stderr)

    if not all_dfs:
        print("No valid data parsed. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Concatenate all DataFrames
    combined = all_dfs[0].append(all_dfs[1:], ignore_index=True)

    # Write output
    out_format = args.format
    if out_format == 'csv':
        out_path = args.output
        if os.path.isdir(out_path):
            out_file = os.path.join(out_path, 'transactions.csv')
        else:
            out_file = out_path
        combined.to_csv(out_file, index=False)
        print(f"Wrote CSV to {out_file}")
    elif out_format == 'json':
        out_path = args.output
        if os.path.isdir(out_path):
            out_file = os.path.join(out_path, 'transactions.json')
        else:
            out_file = out_path
        combined.to_json(out_file, orient='records', date_format='iso')
        print(f"Wrote JSON to {out_file}")
    elif out_format == 'sqlite':
        db_path = args.sqlite_db or 'transactions.db'
        combined.to_sql('transactions', f"sqlite:///{db_path}", if_exists='append', index=False)
        print(f"Wrote data into SQLite DB at {db_path}")
    else:
        print(f"Unknown format: {out_format}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

# FINParser

A Python toolkit for parsing SWIFT `.fin` (e.g., MT940) files into structured data formats. FINParser extracts transaction details, normalizes dates and amounts, and exports to CSV, JSON, or SQLite. It provides both a command‐line interface (CLI) and an optional Tkinter GUI for ease of use.

---

## Table of Contents

* [Features](#features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Directory Structure](#directory-structure)
* [Command‐Line Usage](#command‐line-usage)
* [GUI Usage (Optional)](#gui-usage-optional)
* [Module API](#module-api)
* [Development & Testing](#development--testing)
* [Contributing](#contributing)
* [License](#license)

---

## Features

* **Parse MT940 (SWIFT) files**: Uses the `mt940` library (or any compatible bank‐statement parser) to read `.fin` files.
* **Normalize & Clean Data**: Converts raw transaction tags into a pandas DataFrame, handling dates, debit/credit marks, and descriptions.
* **Multiple Output Formats**: Export combined transaction sets into:

  * CSV (`.csv`)
  * JSON (`.json`)
  * SQLite database (`.db`)
* **Batch Processing**: Accepts one or more `.fin` files in a single command, concatenating transactions across files.
* **Optional GUI**: A simple Tkinter GUI to select files, choose an output format, and view progress.
* **Modular Design**:

  * `parser/fin_reader.py` wraps the specialized parser.
  * `parser/fin_to_df.py` flattens and cleans data into pandas DataFrames.

---

## Requirements

* Python 3.8 or newer
* [pandas](https://pandas.pydata.org/) >= 1.5.0
* [mt940](https://pypi.org/project/mt940/) >= 0.2.1 (or another bank‐statement‐parser)
* (Optional GUI) Python’s built‐in `tkinter` module

You can install dependencies via:

```bash
pip install -r requirements.txt
```

If you prefer to install only the core parsing tools (without GUI):

```bash
pip install pandas mt940
```

---

## Installation

1. **Clone this repository**

   ```bash
   git clone https://github.com/your-username/finparser.git
   cd finparser
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **(Optional) Install as a package**

   ```bash
   pip install .
   ```

   This adds a console script `finparser`, so you can run:

   ```bash
   finparser file1.fin file2.fin --format csv --output ./outdir
   ```

---

## Directory Structure

```
finparser/
├── parser/
│   ├── __init__.py
│   ├── fin_reader.py      # Wraps mt940 (or bank-statement-parser)
│   └── fin_to_df.py       # Converts parsed data into pandas DataFrames
├── cli.py                 # Command-line interface
├── gui.py                 # (Optional) Tkinter GUI application
├── requirements.txt       # Pinned Python dependencies
├── README.md              # This documentation file
├── tests/                 # Unit tests for parsing and DataFrame conversion
│   └── test_parsing.py
└── setup.py               # Package installation script
```

* **`parser/`**: Core modules for reading `.fin` files and converting to DataFrame.
* **`cli.py`**: Entry point for command‐line operations.
* **`gui.py`**: A minimal Tkinter application for file selection and exporting.
* **`tests/`**: pytest tests covering basic parsing logic.

---

## Command‐Line Usage

After installing dependencies, you can run the CLI directly:

```bash
python cli.py [OPTIONS] FILE [FILE ...]
```

If you installed via `pip install .`, use the `finparser` command:

```bash
finparser [OPTIONS] FILE [FILE ...]
```

### Options

```
  FILE                One or more .fin (MT940) files to process.
  -o, --output PATH   Output path (file or directory). Defaults to current directory.
  --format FORMAT     Output format: csv (default), json, sqlite.
  --sqlite-db DB_PATH Path to SQLite DB if --format sqlite. Defaults to ./transactions.db.
```

### Examples

1. **Export to CSV** (output file will be named `transactions.csv` in current directory):

   ```bash
   python cli.py sample1.fin sample2.fin --format csv
   ```

   Or, if installed:

   ```bash
   finparser sample1.fin sample2.fin --format csv
   ```

2. **Specify output directory** (writes `combined.csv` under `./outdir`):

   ```bash
   python cli.py sample1.fin --format csv -o ./outdir
   ```

   If `./outdir` does not exist, create it first:

   ```bash
   mkdir -p outdir
   python cli.py sample1.fin --format csv -o ./outdir
   ```

3. **Export to JSON**:

   ```bash
   python cli.py account1.fin account2.fin --format json -o ./output
   ```

   Resulting file: `./output/transactions.json`.

4. **Export to SQLite**:

   ```bash
   python cli.py account1.fin account2.fin --format sqlite --sqlite-db mydata.db
   ```

   If `--sqlite-db` is omitted, `transactions.db` will be created in the current directory.

After successful parsing, you’ll see console output like:

```
Wrote 42 transactions to output/transactions.csv
```

---

## GUI Usage (Optional)

FINParser includes a minimal Tkinter GUI (`gui.py`) for users who prefer a graphical interface.

### Launching the GUI

1. Ensure you have `tkinter` installed (it’s included by default on most systems).

2. Run:

   ```bash
   python gui.py
   ```

   or, if installed as a package:

   ```bash
   finparser-gui
   ```

3. **Interface Overview**:

   * **Select FIN Files**: Click to open a file picker (multiple selection supported).
   * **Output Format**: Choose between **CSV**, **JSON**, or **SQLite**.
   * **Parse and Export**: Starts the parsing process. A progress bar will run in indeterminate mode until completion.
   * **Results**: On success, a popup shows the output file path (`parsed_transactions.csv`, `parsed_transactions.json`, or `parsed_transactions.db`) in the same directory as the first selected file.

### Example Workflow

1. Launch the GUI:

   ```bash
   python gui.py
   ```
2. Click **Select FIN Files** and choose one or more `.fin` files.
3. Select **CSV** as the output format.
4. Click **Parse and Export**.
5. Once completed, a dialog appears:

   ```
   Successfully wrote CSV to:
   ```

/path/to/parsed\_transactions.csv

````
6. Find your exported CSV in the same folder as the first FIN file.

---

## Module API

If you want to integrate FINParser’s core functionality into another Python project, import from the `parser` package:

```python
from parser import parse_fin_file, transactions_to_dataframe, clean_dataframe
````

### `parse_fin_file(filepath: str) -> List[Statement]`

* **Description**: Reads a `.fin` file (MT940) and returns a list of `mt940.Statement` objects.
* **Arguments**:

  * `filepath`: Path to the `.fin` file.
* **Returns**:

  * A list of `mt940.models.Statement`. Each `Statement` contains attributes like `.account_id`, `.transactions`, `.data['opening_balance']`, etc.

### `transactions_to_dataframe(statements: List[Statement]) -> pandas.DataFrame`

* **Description**: Flattens one or more `Statement` objects into a pandas DataFrame with columns:

  * `account_id`
  * `statement_number`
  * `date`, `entry_date` (as `datetime64[ns]`)
  * `amount` (float; negative for debit, positive for credit)
  * `dc_mark` ( debit/credit indicator )
  * `transaction_type`
  * `customer_reference`
  * `bank_reference`
  * `description`
* **Arguments**:

  * `statements`: List of `mt940.Statement` objects.
* **Returns**:

  * A pandas DataFrame containing all transactions across provided statements.

### `clean_dataframe(df: pandas.DataFrame) -> pandas.DataFrame`

* **Description**: Performs additional cleaning on the DataFrame:

  * Drops duplicate rows.
  * Strips leading/trailing whitespace from string columns.
* **Arguments**:

  * `df`: A DataFrame produced by `transactions_to_dataframe`.
* **Returns**:

  * A cleaned DataFrame.

---

## Development & Testing

### Running Unit Tests

This project uses `pytest` for automated testing. A sample test (in `tests/test_parsing.py`) ensures that parsing and DataFrame conversion work as expected.

1. **Install dev dependencies**

   ```bash
   pip install pytest
   ```

2. **Run tests**

   ```bash
   pytest --maxfail=1 --disable-warnings -q
   ```

If all tests pass, you’ll see output similar to:

```
.                                                                                          [100%]
```

### Code Style & Linters

* Follow **PEP 8** for Python code style.
* You can integrate `flake8` or `black` if preferred. Example:

  ```bash
  pip install flake8 black
  flake8 parser/cli.py parser/fin_reader.py parser/fin_to_df.py
  black parser/ cli.py parser/fin_reader.py parser/fin_to_df.py
  ```

---

## Contributing

Contributions are welcome! To propose changes:

1. Fork the repository.
2. Create a feature branch:

   ```bash
   git checkout -b feature/my-new-feature
   ```
3. Commit your changes with clear messages.
4. Ensure all tests still pass:

   ```bash
   pytest
   ```
5. Push to your fork:

   ```bash
   git push origin feature/my-new-feature
   ```
6. Open a Pull Request describing your changes.

Please follow these guidelines:

* Write clear, concise commit messages.
* Add unit tests for new functionality.
* Update this README if you introduce breaking changes.

---

## License

This project is licensed under the **MIT License**.
See [LICENSE](LICENSE) for full details.

---

## Acknowledgments

* Uses the [mt940](https://pypi.org/project/mt940/) library to parse SWIFT MT940 messages.
* Inspired by open‐source “Bank Statement Parser” tools and common accounting workflows.

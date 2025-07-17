# Crypto Historical Trade Strategy Tester

A command-line tool to backtest trading strategies on historical Kraken OHLCVT data.

## Features
- Buy at a 240, 120, 60, 30, 15, 10, or 5-day low (using the 'low' price).
- Sell when price exceeds buy price by a target percent (with optional tolerance).
- Supports trade fees (optional, configurable percent).
- Handles Kraken OHLCVT files with or without headers.
- Automatically finds available data files if the requested timeframe is missing.
- Exports trade logs to CSV (optional).
- Prints the date range of the historical data used.

## Setup

You can set up the environment in one of two ways:

### Option 1: Using the PowerShell Setup Script (Windows/PowerShell)

1. **Run the provided PowerShell script to automatically set up the virtual environment and install dependencies:**
   ```powershell
   # In PowerShell, from the project directory:
   .\Init-Environment.ps1
   ```
   - To force recreation of the virtual environment, use:
     ```powershell
     .\Init-Environment.ps1 -Recreate
     ```
   - This script will:
     - Create (or recreate) a `.venv` virtual environment in the project directory
     - Upgrade pip
     - Install all dependencies from `requirements.txt`
   - After running, the virtual environment will be activated for the current session.

### Option 2: Manual Setup

1. **Clone the repository and navigate to the project directory:**
   ```sh
   git clone <your-repo-url>
   cd crypto-historical-data-test
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure the data directory:**
   - Copy `.env.example` to `.env`:
     ```sh
     cp .env.example .env
     ```
   - Edit `.env` and set `DATA_ROOT` to the path containing your Kraken OHLCVT CSV files.

4. **Prepare your data:**
   - Download historical Kraken OHLCVT data from the official source:
     [Kraken Downloadable Historical OHLCVT Data](https://support.kraken.com/articles/360047124832-downloadable-historical-ohlcvt-open-high-low-close-volume-trades-data)
   - Save the downloaded CSV files locally on your machine.
   - Place your Kraken OHLCVT files in the data directory. Files should be named like `{pair}_{timeframe}.csv` (e.g., `BTCUSD_1440.csv`).
   - Set the path to your data directory in the `.env` file using the `DATA_ROOT` environment variable. For example:
     ```env
     DATA_ROOT=C:/path/to/your/kraken/data
     ```

## Usage

Run the script with the desired options. Example:

```sh
python main.py \
  --pair BTCUSD \
  --starting-amount 1000 \
  --low-window 30 \
  --target-percent 5 \
  --timeframe 30 \
  --tolerance 0.5 \
  --use-fee \
  --fee-percent 0.2 \
  --output-log-path trade_log.csv
```

### Command Line Arguments
- `--pair` (required): Crypto pair (e.g., BTCUSD, XRPUSDC)
- `--starting-amount` (required): Starting amount in the quote currency (e.g., 1000 USD)
- `--low-window` (required): N-day window for buy signal (choose from 30, 15, 10, 5)
- `--target-percent` (required): Percent gain to trigger sell (e.g., 5 for 5%)
- `--timeframe` (optional, default: 30): Time frame in minutes (choose from 1, 5, 15, 30, 60, 240, 720, 1440)
- `--tolerance` (optional, default: 0.5): Allowed deviation from target percent (e.g., 0.5 for ±0.5%)
- `--use-fee` (optional): If set, apply a fee to each trade
- `--fee-percent` (optional, default: 0.2): Fee percent per trade (e.g., 0.2 for 0.2%)
- `--output-log-path` (optional): Path to export the trade log as CSV

### Output
- Prints the arguments, data file path, and the first 5 rows of loaded data.
- Prints the date range of the historical data used.
- Prints a trade log, total number of trades, and final balance (in the quote currency).
- If `--output-log-path` is provided, exports the trade log to a CSV file.

---

For questions or improvements, open an issue or pull request! 
# Crypto Historical Trade Strategy Tester

## Project Overview

A command-line tool to backtest a trading strategy on historical Kraken OHLCVT data.

**Strategy:**
- Buy at a 30, 15, 10, or 5-day low.
- Sell when price exceeds buy price by a target percent (with tolerance).
- Repeat: buy at next low, sell at next target, etc.
- User provides: crypto pair, starting amount, and strategy parameters.

---

## Key Features & Steps

1. **Command-Line Interface (CLI)**
   - Accepts:
     - Crypto pair (e.g., BTC/USD)
     - Time frame in minutes (1, 5, 15, 30, 60, 240, 720, 1440)
     - Starting amount (e.g., $1000)
     - Strategy parameters (low window, target percent, tolerance)

2. **Data Handling**
   - Load and parse Kraken OHLCVT historical CSV files.
   - Validate and preprocess data (sort, handle missing, etc.).

3. **Strategy Logic**
   - Identify buy points: N-day lows (N = 30, 15, 10, 5).
   - Identify sell points: price exceeds buy by target percent (± tolerance).
   - Simulate trades: update balance, track positions, repeat.

4. **Results & Reporting**
   - Output trade log (buy/sell dates, prices, profit/loss).
   - Final balance and performance metrics.
   - Optionally, export results to CSV.

5. **Extensibility**
   - Easy to add new strategies or parameters in the future.

---

## Suggested File Structure

```
crypto-historical-data-test/
│
├── main.py                # CLI entry point
├── data_loader.py         # Load & preprocess Kraken data
├── strategy.py            # Implements trading logic
├── simulator.py           # Runs the backtest loop
├── report.py              # Output and reporting utilities
├── requirements.txt       # Dependencies
└── README.md              # Project overview & usage
```

---

## Next Steps

1. Confirm or adjust the above plan and file structure.
2. Decide on the programming language (Python is ideal for this).
3. Choose CLI library (argparse, click, typer, etc.).
4. Specify any additional features or constraints (e.g., multi-threading, plotting, etc.).

## Updates

- **Data Directory Configuration:**
  - The root data directory will be set in a `.env` file (e.g., `DATA_ROOT=/absolute/path/to/kraken/data`).
  - The script will read this configuration at startup to locate the data files.
  - The CLI will not require the data directory as a parameter.
  - Data files will be accessed as `{DATA_ROOT}/{pair}_{timeframe}.csv`.

- **Time Frame Parameter:**
  - The CLI will accept a `time frame in minutes` parameter (allowed: 1, 5, 15, 30, 60, 240, 720, 1440).

- **OHLCVT File Format:**
  - Each row: `<timestamp>,<open>,<high>,<low>,<close>,<volume>,<trades>`

---

## Updated CLI Parameters

- Crypto pair (e.g., BTCUSD)
- Time frame in minutes (1, 5, 15, 30, 60, 240, 720, 1440)
- Starting amount
- Strategy parameters (low window, target percent, tolerance) 
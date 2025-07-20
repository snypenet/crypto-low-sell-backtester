import argparse
from data_loader import get_data_file_path, load_ohlcvt_data
from window_low_strategy import window_low_strategy
from window_low_average_strategy import window_low_average_strategy
from window_low_ema_strategy import window_low_ema_strategy
import pandas as pd
from datetime import datetime, UTC

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crypto Historical Trade Strategy Tester")
    parser.add_argument("--pair", required=True, help="Crypto pair (e.g., BTCUSD)")
    parser.add_argument("--timeframe", type=int, default=30, choices=[1, 5, 15, 30, 60, 240, 720, 1440], help="Time frame in minutes (default: 30)")
    parser.add_argument("--starting-amount", type=float, required=True, help="Starting amount (e.g., 1000)")
    parser.add_argument("--low-window", type=int, required=True, choices=[240, 120, 60, 30, 15, 10, 5], help="Low window in days")
    parser.add_argument("--target-percent", type=float, required=True, help="Target percent gain for selling (e.g., 5 for 5%)")
    parser.add_argument("--tolerance", type=float, default=0.5, help="Tolerance for target percent (default: 0.5)")
    parser.add_argument("--output-log-path", type=str, default=None, help="Optional path to export the trade log as CSV")
    parser.add_argument("--use-fee", action="store_true", help="If set, apply a fee to each trade")
    parser.add_argument("--fee-percent", type=float, default=0.2, help="Fee percent per trade (default: 0.2)")
    parser.add_argument("--strategy", type=str, default="window_low", choices=["window_low", "window_low_average", "window_low_ema"], help="Strategy type to use (default: window_low)")

    args = parser.parse_args()

    print("Arguments:", args)
    data_file_path = get_data_file_path(args.pair, args.timeframe)
    print("Data file path:", data_file_path)

    try:
        df = load_ohlcvt_data(args.pair, args.timeframe)
        print("Loaded data (first 5 rows):")
        print(df.head())

        # Log the starting and ending date of the historical data
        if not df.empty:
            start_ts = int(df.iloc[0]['timestamp'])
            end_ts = int(df.iloc[-1]['timestamp'])
            start_date = datetime.fromtimestamp(start_ts, UTC).strftime('%Y-%m-%d %H:%M:%S')
            end_date = datetime.fromtimestamp(end_ts, UTC).strftime('%Y-%m-%d %H:%M:%S')
            print(f"Data range: {start_date} to {end_date} (UTC)")

        # Run selected strategy
        if args.strategy == "window_low":
            trade_log, final_balance = window_low_strategy(
                df,
                args.starting_amount,
                args.low_window,
                args.target_percent,
                args.tolerance,
                use_fee=args.use_fee,
                fee_percent=args.fee_percent
            )
        elif args.strategy == "window_low_average":
            trade_log, final_balance = window_low_average_strategy(
                df,
                args.starting_amount,
                args.low_window,
                args.target_percent,
                args.tolerance,
                use_fee=args.use_fee,
                fee_percent=args.fee_percent
            )
        elif args.strategy == "window_low_ema":
            trade_log, final_balance = window_low_ema_strategy(
                df,
                args.starting_amount,
                args.low_window,
                args.target_percent,
                args.tolerance,
                use_fee=args.use_fee,
                fee_percent=args.fee_percent
            )
        else:
            raise ValueError(f"Unknown strategy: {args.strategy}")

        print("\nTrade Log:")
        for trade in trade_log:
            print(trade)
        print(f"\nTotal trades: {len(trade_log)}")
        print(f"Final balance: {final_balance:.2f}")

        # Optional CSV export
        if args.output_log_path:
            pd.DataFrame(trade_log).to_csv(args.output_log_path, index=False)
            print(f"Trade log exported to {args.output_log_path}")
    except Exception as e:
        print(f"Error: {e}") 
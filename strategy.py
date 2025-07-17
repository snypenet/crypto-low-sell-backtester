import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

def simulate_strategy(
    df: pd.DataFrame,
    starting_amount: float,
    low_window: int,
    target_percent: float,
    tolerance: float,
    use_fee: bool = False,
    fee_percent: float = 0.2
) -> Tuple[List[Dict[str, Any]], float]:
    """
    N‑day‑low buy/sell strategy, stepping one *calendar* day at a time.

    Steps (condensed):
      1. Start at first date + low_window.
      2. Each day, look back low_window days (exclusive of from_date, inclusive of to_date)
         and get the window low.
      3. Buy when today’s low < previous window low.
      4. After buying, advance day‑by‑day until any intraday *high* meets the
         target gain (± tolerance) and sell.
      5. Repeat until the last date.  If still holding at the end, sell at final close.
    """
    trade_log: List[Dict[str, Any]] = []
    balance = starting_amount
    position = 0.0
    fee_mult = 1 - (fee_percent / 100.0) if use_fee else 1.0

    # Normalise dates
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df['date'] = df['datetime'].dt.date

    first_date = df['date'].min()
    last_date  = df['date'].max()
    current_date = first_date + timedelta(days=low_window)

    next_row_idx = 0          # ensures monotonic forward scan
    prev_window_low = None    # lowest price in the last completed window

    while current_date <= last_date:
        # --- 1. compute look‑back window ---
        from_date = current_date - timedelta(days=low_window)
        to_date   = current_date
        window_mask = (df['date'] > from_date) & (df['date'] <= to_date) & (df.index >= next_row_idx)
        window_rows = df[window_mask]
        if window_rows.empty:
            # no trades at all in look‑back → skip forward a day
            current_date += timedelta(days=1)
            continue

        window_low = window_rows['low'].min()

        # --- 2. today’s trades ---
        day_rows = df[(df['date'] == current_date) & (df.index >= next_row_idx)]
        if day_rows.empty:
            # still update sliding low then move on
            prev_window_low = window_low
            current_date += timedelta(days=1)
            continue

        day_low = day_rows['low'].min()

        # --- 3. BUY logic ---
        if position == 0.0 and prev_window_low is not None and day_low < prev_window_low:
            buy_row   = day_rows[day_rows['low'] == day_low].iloc[0]
            buy_price = buy_row['low']
            qty       = (balance / buy_price) * fee_mult
            fee_paid  = (balance / buy_price) * (fee_percent / 100.0) if use_fee else 0.0

            position = qty
            balance  = 0.0
            trade_log.append({
                'type': 'buy',
                'timestamp': buy_row['timestamp'],
                'price': buy_price,
                'amount': qty,
                'fee': fee_paid
            })

            # --- 4. SELL search ---
            min_price = buy_price * (1 + (target_percent - tolerance) / 100.0)
            sold      = False
            sell_date = current_date + timedelta(days=1)

            while sell_date <= last_date and not sold:
                sell_rows = df[(df['date'] == sell_date) & (df.index > buy_row.name)]
                for idx, row in sell_rows.iterrows():
                    sell_price = row['high']          # <-- intraday high
                    if sell_price >= min_price:
                        gross_cash = position * sell_price
                        fee_paid   = gross_cash * (fee_percent / 100.0) if use_fee else 0.0
                        balance    = gross_cash * fee_mult
                        trade_log.append({
                            'type': 'sell',
                            'timestamp': row['timestamp'],
                            'price': sell_price,
                            'amount': position,
                            'fee': fee_paid
                        })
                        position      = 0.0
                        current_date  = sell_date + timedelta(days=1)
                        next_row_idx  = idx + 1
                        sold = True
                        break
                sell_date += timedelta(days=1)

            if not sold:
                # Ran to end without hitting target; exit loop and final‑sell later
                break

            # force window recalculation on next pass
            prev_window_low = None
            continue   # back to main while‑loop

        # --- 5. advance day when no buy or already holding ---
        prev_window_low = window_low
        current_date   += timedelta(days=1)

    # --- 6. Close open position at end of file ---
    if position > 0.0:
        last_row    = df.iloc[-1]
        gross_cash  = position * last_row['close']
        fee_paid    = gross_cash * (fee_percent / 100.0) if use_fee else 0.0
        balance     = gross_cash * fee_mult
        trade_log.append({
            'type': 'sell',
            'timestamp': last_row['timestamp'],
            'price': last_row['close'],
            'amount': position,
            'fee': fee_paid
        })

    return trade_log, balance

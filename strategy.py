import pandas as pd
from typing import List, Dict, Any, Tuple

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
    Simulate the buy-at-N-day-low, sell-at-target strategy.
    Uses the 'low' price for N-day low detection and for buying.
    Uses the 'close' price for selling.
    Args:
        df: OHLCVT DataFrame (must be validated and sorted)
        starting_amount: Initial cash balance
        low_window: N-day window for buy signal
        target_percent: Percent gain to trigger sell (e.g., 5 for 5%)
        tolerance: Allowed deviation from target percent (e.g., 0.5 for ±0.5%)
        use_fee: Whether to apply a fee to each trade
        fee_percent: Fee percent per trade (e.g., 0.2 for 0.2%)
    Returns:
        trade_log: List of trade dicts (buy/sell info)
        final_balance: Cash balance after simulation
    """
    trade_log = []
    balance = starting_amount
    position = 0.0  # Amount of asset held
    i = low_window  # Start after we have enough data for the first window
    n = len(df)
    fee_mult = 1 - (fee_percent / 100.0) if use_fee else 1.0

    while i < n:
        # Look for N-day low (using 'low' price)
        window = df.iloc[i - low_window:i]
        current_low = df.iloc[i]['low']
        is_n_day_low = current_low == window['low'].min()

        if position == 0.0 and is_n_day_low:
            # Buy at this low price
            buy_price = current_low
            amount_bought = (balance / buy_price) * fee_mult
            fee_paid = (balance / buy_price) * (fee_percent / 100.0) if use_fee else 0.0
            position = amount_bought
            buy_time = df.iloc[i]['timestamp']
            trade_log.append({
                'type': 'buy',
                'timestamp': buy_time,
                'price': buy_price,
                'amount': amount_bought,
                'fee': fee_paid
            })
            balance = 0.0

            # Now look for sell opportunity
            min_price = buy_price * (1 + (target_percent - tolerance) / 100.0)
            max_price = buy_price * (1 + (target_percent + tolerance) / 100.0)
            sold = False
            for j in range(i + 1, n):
                sell_price = df.iloc[j]['close']
                if min_price <= sell_price <= max_price:
                    # Sell at this price
                    sell_time = df.iloc[j]['timestamp']
                    gross_cash = position * sell_price
                    fee_paid = gross_cash * (fee_percent / 100.0) if use_fee else 0.0
                    net_cash = gross_cash * fee_mult
                    balance = net_cash
                    trade_log.append({
                        'type': 'sell',
                        'timestamp': sell_time,
                        'price': sell_price,
                        'amount': position,
                        'fee': fee_paid
                    })
                    position = 0.0
                    i = j  # Continue from here
                    sold = True
                    break
            if not sold:
                # Never hit target, exit loop
                break
        else:
            i += 1

    # If still holding position at the end, sell at last close
    if position > 0.0:
        sell_price = df.iloc[-1]['close']
        sell_time = df.iloc[-1]['timestamp']
        gross_cash = position * sell_price
        fee_paid = gross_cash * (fee_percent / 100.0) if use_fee else 0.0
        net_cash = gross_cash * fee_mult
        balance = net_cash
        trade_log.append({
            'type': 'sell',
            'timestamp': sell_time,
            'price': sell_price,
            'amount': position,
            'fee': fee_paid
        })
        position = 0.0

    return trade_log, balance 
# backtester.py
import pandas as pd
import datetime
import config
from strategy import Strategy

def run_backtest(historical_file):
    """
    Backtests the strategy using historical option data.
    Assumes the CSV has columns: Timestamp, UnderlyingPrice, OptionType, Strike, LTP, Volume.
    """
    df = pd.read_csv(historical_file, parse_dates=['Timestamp'])
    df.sort_values("Timestamp", inplace=True)
    # For simulation, set a fixed expiry date (modify as needed)
    expiry_date = datetime.datetime.strptime("24-Apr-2025", "%d-%b-%Y")
    strategy = Strategy(config.TRADING_CONFIG)
    position_open = False
    trade_logs = []
    entry_trade = None
    previous_straddle = None

    grouped = df.groupby("Timestamp")
    for timestamp, group in grouped:
        try:
            call_row = group[group["OptionType"] == "CE"].iloc[0]
            put_row  = group[group["OptionType"] == "PE"].iloc[0]
        except Exception:
            continue

        atm_call_price = call_row["LTP"]
        atm_call_volume = call_row["Volume"]
        atm_put_price = put_row["LTP"]
        atm_put_volume = put_row["Volume"]
        current_straddle = atm_call_price + atm_put_price
        avwap_straddle, avwap_call, avwap_put = strategy.update_vwap(atm_call_price, atm_call_volume, atm_put_price, atm_put_volume)

        if not position_open:
            if strategy.check_entry_condition(atm_call_price, atm_put_price, avwap_straddle, avwap_call, avwap_put, previous_straddle):
                entry_trade = {
                    "entry_time": timestamp,
                    "atm_call_price": atm_call_price,
                    "atm_put_price": atm_put_price,
                    "avwap_straddle": avwap_straddle
                }
                trade_logs.append({"Time": timestamp, "Event": "ENTER", "Details": entry_trade})
                position_open = True
        else:
            entry_straddle = entry_trade["atm_call_price"] + entry_trade["atm_put_price"]
            pnl = (entry_straddle - current_straddle)  # per unit; multiply by lot size later if desired
            if strategy.should_exit_based_on_avwap(current_straddle, avwap_straddle, previous_straddle):
                exit_trade = {
                    "exit_time": timestamp,
                    "exit_straddle": current_straddle,
                    "pnl": pnl
                }
                trade_logs.append({"Time": timestamp, "Event": "EXIT", "Details": exit_trade})
                position_open = False
        previous_straddle = current_straddle

    print("Backtest Results:")
    for log in trade_logs:
        print(log)

if __name__ == "__main__":
    historical_file = config.BACKTEST_DATA_DIR + "/sample_day.csv"
    run_backtest(historical_file)

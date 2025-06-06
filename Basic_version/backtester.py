# backtester.py
import os
import pandas as pd
import datetime
import config
from strategy import Strategy
from data_fetcher import DataFetcher

def download_historical_data(client, scrip_code, timeframe, from_date, to_date):
    """
    Downloads historical data using the 5paisa historical_data API.
    Parameters:
       scrip_code: Integer representing the instrument code (e.g., 1660)
       timeframe: One of ['1m','5m','10m','15m','30m','60m','1d']
       from_date: Start date string in 'YYYY-MM-DD' format.
       to_date: End date string in 'YYYY-MM-DD' format.
    Returns:
       A pandas DataFrame containing the historical data.
    """
    # Calling the historical_data API as defined:
    # historical_data(Exchange, Exchange Type, Scrip Code, Time Frame, From Date, To Date)
    df = client.historical_data('N', 'C', scrip_code, timeframe, from_date, to_date)
    return df

def get_backtest_data():
    """
    Checks if the backtest data file exists; if not, downloads historical data using the 5paisa API.
    Returns the path to the CSV file.
    """
    # Ensure the backtest data directory exists.
    if not os.path.exists(config.BACKTEST_DATA_DIR):
        os.makedirs(config.BACKTEST_DATA_DIR)
    
    filename = os.path.join(config.BACKTEST_DATA_DIR, "sample_day.csv")
    
    if not os.path.exists(filename):
        print("Historical data file not found. Downloading historical data...")
        # Adjust these dates and timeframe as needed.
        from_date = "2021-05-25"
        to_date = "2021-06-16"
        timeframe = "15m"
        scrip_code = 1660  # Replace with the appropriate Scrip Code for your instrument
        
        # Initialize DataFetcher to get access to the 5paisa client.
        data_fetcher = DataFetcher(config.API_CONFIG)
        df = download_historical_data(data_fetcher.client, scrip_code, timeframe, from_date, to_date)
        
        # Save DataFrame to CSV in the backtest data directory.
        df.to_csv(filename, index=False)
        print(f"Historical data saved to {filename}")
    else:
        print("Historical data file found.")
    return filename

def run_backtest(historical_file):
    """
    Runs a backtest using historical data contained in the CSV file.
    Assumes the CSV file has at least the following columns:
       Datetime, UnderlyingPrice, OptionType, Strike, LTP, Volume
    """
    # Updated parse_dates to use the column "Datetime"
    df = pd.read_csv(historical_file, parse_dates=['Datetime'])
    df.sort_values("Datetime", inplace=True)
    
    # Set a fixed expiry date for simulation (modify as needed)
    expiry_date = datetime.datetime.strptime("24-Apr-2025", "%d-%b-%Y")
    
    strategy = Strategy(config.TRADING_CONFIG)
    position_open = False
    trade_logs = []
    entry_trade = None
    previous_straddle = None

    # Group by the "Datetime" column (assuming each group contains data for both CE and PE options)
    grouped = df.groupby("Datetime")
    for dt, group in grouped:
        try:
            # Get the call row and put row for the ATM option.
            call_row = group[group["OptionType"] == "CE"].iloc[0]
            put_row  = group[group["OptionType"] == "PE"].iloc[0]
        except Exception as e:
            continue

        atm_call_price = call_row["LTP"]
        atm_call_volume = call_row["Volume"]
        atm_put_price = put_row["LTP"]
        atm_put_volume = put_row["Volume"]
        current_straddle = atm_call_price + atm_put_price

        # Update AVWAP calculations.
        avwap_straddle, avwap_call, avwap_put = strategy.update_vwap(
            atm_call_price, atm_call_volume, atm_put_price, atm_put_volume
        )

        if not position_open:
            if strategy.check_entry_condition(atm_call_price, atm_put_price, avwap_straddle, avwap_call, avwap_put, previous_straddle):
                entry_trade = {
                    "entry_time": dt,
                    "atm_call_price": atm_call_price,
                    "atm_put_price": atm_put_price,
                    "avwap_straddle": avwap_straddle
                }
                trade_logs.append({"Datetime": dt, "Event": "ENTER", "Details": entry_trade})
                position_open = True
        else:
            entry_straddle = entry_trade["atm_call_price"] + entry_trade["atm_put_price"]
            pnl = (entry_straddle - current_straddle)  # per unit; scale by lot size if required
            if strategy.should_exit_based_on_avwap(current_straddle, avwap_straddle, previous_straddle):
                exit_trade = {
                    "exit_time": dt,
                    "exit_straddle": current_straddle,
                    "pnl": pnl
                }
                trade_logs.append({"Datetime": dt, "Event": "EXIT", "Details": exit_trade})
                position_open = False

        previous_straddle = current_straddle

    print("Backtest Results:")
    for log in trade_logs:
        print(log)

if __name__ == "__main__":
    historical_file = get_backtest_data()
    run_backtest(historical_file)

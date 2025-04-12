# main.py
import time
import datetime
import config
from data_fetcher import DataFetcher
from strategy import Strategy
from execution import OrderExecutor
from risk_manager import RiskManager
from logger import CSVLogger

def main():
    # Initialize the logger
    logger = CSVLogger(config.LOG_FILE_PATH, config.DASHBOARD_CSV_PATH)
    logger.log_event("SYSTEM_START", "Starting Iron Condor Trading Bot")

    # Initialize data fetcher (which logs in via TOTP)
    data_fetcher = DataFetcher(config.API_CONFIG)
    
    # Fetch latest expiry and option chain
    expiry = data_fetcher.get_latest_monthly_expiry()
    logger.log_event("INFO", f"Latest expiry detected: {expiry}")
    option_chain = data_fetcher.get_option_chain()
    underlying_price = data_fetcher.get_underlying_price()
    logger.log_event("INFO", f"Underlying BankNifty price: {underlying_price}")
    
    # Initialize strategy, order executor, and risk manager
    strategy = Strategy(config.TRADING_CONFIG)
    order_executor = OrderExecutor(data_fetcher.client, config.TRADING_CONFIG, logger)
    risk_manager = RiskManager(config.TRADING_CONFIG, logger)
    
    position_open = False
    trade_setup = None
    previous_straddle = None
    entry_trade_straddle = None
    
    # Set trading end time (assumed to be today at specified time)
    trading_end_time = datetime.datetime.strptime(config.TRADING_CONFIG["trading_end_time"], "%H:%M").time()
    
    while datetime.datetime.now().time() < trading_end_time:
        try:
            # Refresh underlying price and option chain
            underlying_price = data_fetcher.get_underlying_price()
            option_chain = data_fetcher.get_option_chain()
            
            # Determine trade setup (selected strikes) using strategy logic.
            trade_setup = strategy.select_strikes(option_chain, underlying_price, 
                                                  datetime.datetime.combine(datetime.date.today(), trading_end_time))
            
            # Get live quotes for the ATM call and put.
            quote_call = data_fetcher.client.get_quote_by_scrip(trade_setup["atm_call"]['ScripCode'])
            quote_put  = data_fetcher.client.get_quote_by_scrip(trade_setup["atm_put"]['ScripCode'])
            atm_call_price = float(quote_call.get("LTP", 0))
            atm_put_price = float(quote_put.get("LTP", 0))
            atm_call_volume = float(quote_call.get("Volume", 100))
            atm_put_volume = float(quote_put.get("Volume", 100))
            
            # Update AVWAP values.
            avwap_straddle, avwap_call, avwap_put = strategy.update_vwap(atm_call_price, atm_call_volume, atm_put_price, atm_put_volume)
            current_straddle = atm_call_price + atm_put_price
            logger.log_event("DATA_UPDATE", f"Straddle: {current_straddle}, AVWAP: {avwap_straddle}")
            
            if not position_open:
                if strategy.check_entry_condition(atm_call_price, atm_put_price, avwap_straddle, avwap_call, avwap_put, previous_straddle):
                    logger.log_event("ENTRY_SIGNAL", f"Entry conditions met. Straddle: {current_straddle} < AVWAP: {avwap_straddle}")
                    order_ids = order_executor.execute_iron_condor(trade_setup)
                    position_open = True
                    entry_trade_straddle = current_straddle
                    logger.update_dashboard("Position Open", 0, f"Entry at straddle {current_straddle}")
            else:
                # Simple PnL calculation: (entry_straddle - current_straddle)*lot_size*num_lots
                current_pnl = (entry_trade_straddle - current_straddle) * config.TRADING_CONFIG["lot_size"] * config.TRADING_CONFIG["num_lots"]
                risk_trigger = risk_manager.check_risk()
                exit_signal = risk_manager.should_exit_based_on_avwap(current_straddle, avwap_straddle, previous_straddle)
                if risk_trigger or exit_signal:
                    reason = risk_trigger if risk_trigger else "AVWAP breakout"
                    logger.log_event("EXIT_SIGNAL", f"Exiting due to {reason}; current_pnl: {current_pnl}")
                    order_ids = order_executor.exit_position(trade_setup)
                    logger.update_dashboard("Position Closed", current_pnl, f"Exited with orders: {order_ids}")
                    position_open = False
            previous_straddle = current_straddle
        except Exception as e:
            logger.log_event("ERROR", f"Exception in main loop: {str(e)}")
        time.sleep(config.TRADING_CONFIG["data_update_interval"])
    
    logger.log_event("SYSTEM_END", "Trading session ended. Exiting.")

if __name__ == "__main__":
    main()

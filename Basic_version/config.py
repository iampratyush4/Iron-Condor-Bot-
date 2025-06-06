# config.py
import os

# ------------------------------
# API and Authentication Config with TOTP
# ------------------------------
API_CONFIG = {
	"APP_NAME":"5P53700772",
	"APP_SOURCE":"5793",
	"USER_ID":"U5XLxxpPP7g",
	"PASSWORD":"fHzfCHaxIIu",
	"USER_KEY":"G0RNtcBkVTKDfvokfStElzPT7X6qthAw",
	"ENCRYPTION_KEY":"YbuTd5c0SMSRAEvJliCPVY8hVBYdHXZH",
    "CLIENT_CODE": "53700772",  # 5paisa client code                 # 6-digit TOTP from your authenticator app
    "PIN": "525625",
}

Cred ={
    "APP_NAME":"5P53700772",
	"APP_SOURCE":"5793",
	"USER_ID":"U5XLxxpPP7g",
	"PASSWORD":"fHzfCHaxIIu",
	"USER_KEY":"G0RNtcBkVTKDfvokfStElzPT7X6qthAw",
	"ENCRYPTION_KEY":"YbuTd5c0SMSRAEvJliCPVY8hVBYdHXZH"
}

# ------------------------------
# Trading parameters
# ------------------------------
TRADING_CONFIG = {
    "capital": 100000,            # Capital allocation in INR for the strategy
    "stop_loss_pct": 5,           # Maximum allowed loss as % of capital
    "target_pct": 5,              # Profit target as % of capital
    "lot_size": 25,               # Bank Nifty option lot size
    "num_lots": 1,                # Number of lots to trade
    "max_retries": 3,             # Maximum number of order placement retries
    "avwap_anchor_time": "09:15", # Time (HH:MM) to anchor the VWAP (typically market open)
    "data_update_interval": 1,    # Data update interval in seconds
    "check_exit_interval": 60,    # Interval in seconds to check exit conditions
    "trading_start_time": "09:15",
    "trading_end_time": "15:30"
}

# ------------------------------
# Files for Logging and Dashboard
# ------------------------------
LOG_FILE_PATH = "trade_log.csv"
DASHBOARD_CSV_PATH = "dashboard.csv"

# ------------------------------
# Backtesting configuration
# ------------------------------
BACKTEST_DATA_DIR = "historical_data"  # Directory containing historical CSV files

# Iron Condor Trading Bot for 5paisa

This project is a production‑grade automated trading system for implementing an options Iron Condor strategy on Bank Nifty via the 5paisa API. It is designed to use real‑time option chain data, TOTP‑based login, dynamic trade execution, anchored VWAP (AVWAP) analysis, and robust risk management. In addition, a backtesting module is provided for historical simulation.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
  - [1. Data Fetching and TOTP Login](#data-fetching-and-totp-login)
  - [2. Strategy Logic and AVWAP](#strategy-logic-and-avwap)
  - [3. Order Execution](#order-execution)
  - [4. Risk Management](#risk-management)
  - [5. Logging and Dashboard](#logging-and-dashboard)
  - [6. Backtesting Module](#backtesting-module)
  - [7. Live Trading Loop](#live-trading-loop)
- [Replication and Running the Code](#replication-and-running-the-code)
- [Notes and Further Improvements](#notes-and-further-improvements)
- [License](#license)

---

## Overview

The Iron Condor Trading Bot automatically executes and manages an Iron Condor options strategy on Bank Nifty. It uses the official 5paisa API for:

- **Authentication via TOTP:** Secure login using one‑time passwords.
- **Fetching Real‑Time Option Chain Data:** Obtaining the latest Bank Nifty option chain and determining the monthly expiry.
- **Anchored VWAP Calculation:** Computing the volume‑weighted average price (AVWAP) for the ATM straddle and individual legs. The AVWAP is used to verify that the trade entry conditions are met—namely, that the current premium is below its historical average as determined from the session’s start.
- **Delta-Based Strike Selection:** Automatically picking short options (~4 delta) and corresponding hedge options (~2 delta) for both calls and puts.
- **Automatic Order Execution:** Placing a basket of four orders (two buys for hedges, two sells for the short positions) with retries on error.
- **Risk Management:** Monitoring live positions for stop‑loss and profit target conditions, as well as exit signals based on an AVWAP breakout.
- **Logging and Dashboard:** Keeping a detailed CSV log for each action and a simple dashboard CSV for live status tracking.
- **Backtesting:** A separate module downloads historical option chain data automatically (using 5paisa’s historical_data API) and runs a simulation over past data, enabling testing and parameter tuning.

---

## Features

- **TOTP‑Based Authentication:** Secure login to the 5paisa API using client credentials and a 6‑digit TOTP.
- **Real‑Time Data Acquisition:** Retrieves the latest monthly expiry and option chain for Bank Nifty, plus the underlying index price.
- **Dynamic Strategy Execution:** Calculates anchored VWAP values, monitors market conditions, and automatically executes orders based on predefined conditions.
- **Robust Order Management:** Uses retry logic for order placement and monitors the status of multi‑leg orders.
- **Risk Controls:** Implements stop‑loss and profit target checks as well as AVWAP breakout logic.
- **Detailed Logging:** Writes detailed events (e.g., order placements, entry/exit signals, errors) to a CSV log file along with a dashboard CSV for a quick view.
- **Historical Data Backtesting:** Downloads historical data from 5paisa if necessary and simulates trading logic on that data.

---

## Directory Structure

```
iron_condor_bot/
├── config.py           # Contains API credentials, trading parameters, and file paths.
├── data_fetcher.py     # Handles login (TOTP-based) and data retrieval (option chain, underlying price).
├── strategy.py         # Implements the trading strategy: AVWAP calculation, delta calculation, entry condition, and strike selection.
├── execution.py        # Contains order execution logic including placing orders and handling retries.
├── risk_manager.py     # Monitors trade PnL and checks for stop-loss, profit target, and exit conditions.
├── logger.py           # Logs events to CSV files and updates a dashboard CSV.
├── backtester.py       # Downloads historical data (using 5paisa's historical_data API) and runs a simulation over historical data.
└── main.py             # The main live trading loop orchestrating data updates, strategy checks, order execution, and risk management.
```

---

## Setup and Installation

1. **Install Python:**  
   This code is written for Python 3. Install Python (e.g., Python 3.9 or later).

2. **Clone the Repository:**  
   ```bash
   git clone https://github.com/yourusername/Iron-Condor-Bot-.git
   cd Iron-Condor-Bot-
   ```

3. **Create a Virtual Environment and Activate It:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install Dependencies:**  
   Create a `requirements.txt` file (if not already provided) with the following content:
   ```
   numpy
   pandas
   scipy
   py5paisa
   ```
   Then run:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

Open `config.py` and update the following parameters:
- **API_CONFIG:**  
  Replace placeholder values (`"your_user_id"`, `"YourTOTP"`, etc.) with your actual 5paisa credentials. The TOTP value can be provided via environment variable or entered at runtime.
- **TRADING_CONFIG:**  
  Adjust parameters such as `capital`, `stop_loss_pct`, `target_pct`, `lot_size`, and trading times as desired.
- **File Paths:**  
  Review `LOG_FILE_PATH`, `DASHBOARD_CSV_PATH`, and `BACKTEST_DATA_DIR` if you want to store logs/data in specific folders.

---

## How It Works

### 1. Data Fetching and TOTP Login

- **data_fetcher.py:**  
  Instantiates a `FivePaisaClient` using a credentials dictionary (from `config.py`), and performs a TOTP-based login via `get_totp_session()`. It provides functions to fetch:
  - **Latest monthly expiry:** Chooses the expiry that is the last Thursday of the current month.
  - **Option chain data:** Retrieves full option chain details for BANKNIFTY.
  - **Underlying price:** Fetches the current BANKNIFTY price.

### 2. Strategy Logic and AVWAP

- **strategy.py:**  
  Implements an `AVWAPCalculator` that continuously updates the anchored VWAP (volume‑weighted average price) using incoming price and volume data from the ATM call and put options. It also includes:
  - **Delta Calculation:** Using the Black‑Scholes formula (via `calculate_delta()`) to determine the approximate delta.
  - **Entry Condition:** Checks if the combined ATM straddle price is below its AVWAP and if individual ATM option prices are below their respective AVWAPs.
  - **Strike Selection:** Parses the option chain to select the ATM option, the 4‑delta short options, and the corresponding 2‑delta hedges.

### 3. Order Execution

- **execution.py:**  
  Contains the `OrderExecutor` class, which uses the 5paisa API method `place_order()` to place market orders. Orders are placed in sequence:
  - **Hedges are placed first** (buy orders for the far OTM options).
  - **Then short orders** for the 4‑delta options.
  Retry logic ensures orders are re‑attempted if they fail.

### 4. Risk Management

- **risk_manager.py:**  
  Monitors the running mark‑to‑market P&L for the open trade and checks for triggers such as:
  - **Stop‑loss:** Exit if losses exceed the configured threshold.
  - **Profit target:** Exit if profits exceed the target.
  - **AVWAP Breakout:** Exits the trade if the ATM straddle price breaks above its AVWAP, signaling potential volatility changes.

### 5. Logging and Dashboard

- **logger.py:**  
  Logs every action (e.g., order placements, signal triggers, errors) to a CSV file for audit. It also updates a “dashboard” CSV file to summarize the current trade status (open/closed, current PnL, etc.) for quick review.

### 6. Backtesting Module

- **backtester.py:**  
  Checks if a historical data CSV exists in the specified directory. If not, it automatically downloads data using the 5paisa API method:  
  ```python
  historical_data('N', 'C', <Scrip Code>, <Time Frame>, <From Date>, <To Date>)
  ```  
  Once downloaded, it saves the file and runs a simulation over it—using the same AVWAP and entry/exit logic—to generate trade logs.

### 7. Live Trading Loop

- **main.py:**  
  Orchestrates the entire live trading process:
  - It initializes the data fetcher (which logs in via TOTP), retrieves live option chain data, and calculates entry conditions.
  - When conditions are met, it places the orders using the order executor.
  - It then monitors the position’s P&L, checking for risk or AVWAP-triggered exits.
  - All activities are logged and the dashboard CSV is updated in near real‑time.

---

## Replication and Running the Code

1. **Clone the Repository:**  
   Follow the instructions in the [Setup and Installation](#setup-and-installation) section.

2. **Set Up Your Credentials:**  
   Update `config.py` with your correct API credentials (including TOTP and PIN).

3. **Install Dependencies:**  
   Run `pip install -r requirements.txt`.

4. **Run Backtester:**  
   To download historical option chain data and run a simulation:
   ```bash
   python backtester.py
   ```
   Check the console output and the generated log files for trade simulation results.

5. **Run Live Trading Simulation (Paper Trading):**  
   If available, run:
   ```bash
   python main.py
   ```
   This will start the live trading loop. **Make sure to test thoroughly in a safe environment first.**

6. **Monitor Logs and Dashboard:**  
   - **trade_log.csv:** Contains detailed logs of each action.
   - **dashboard.csv:** Provides a quick status view.

---

## Notes and Further Improvements

- **SDK Verification:**  
  The code assumes that the 5paisa SDK (py5paisa) provides certain API methods (e.g., `get_option_chain`, `get_quote_by_scrip`, `place_order`, `historical_data`). Verify these in the official documentation and adjust if necessary.

- **Data Accuracy:**  
  Ensure that the downloaded historical data includes all necessary columns (e.g., `Datetime`, `OptionType`, `Strike`, `LTP`, `Volume`, `ScripCode`).  
  The backtester is designed for multi‑leg option strategy simulation.

- **P&L Calculation:**  
  The current P&L computation in live trading is simplified. For more accuracy, consider calculating each leg’s profit separately.

- **Asynchronous Handling:**  
  For ultra‑low latency and robust order execution, consider integrating asynchronous order status callbacks, if supported by the API.

- **Environment-Specific Adjustments:**  
  Modify trading start and end times, risk thresholds, and lot sizes to suit your specific requirements.

---

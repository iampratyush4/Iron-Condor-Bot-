class TradingConfig:
    # Core parameters
    CAPITAL = 10_000_000  # $10M
    MAX_RISK_PER_TRADE = 0.01  # 1% of capital
    LOT_SIZE = 25
    NUM_LOTS = 40
    
    # Adaptive parameters
    VOL_REGIME_THRESHOLDS = {
        "low": 0.15,
        "medium": 0.30,
        "high": 0.45
    }
    
    # Execution parameters
    ORDER_TYPES = {
        "LIQUID": "MARKET",
        "ILLIQUID": "LIMIT"
    }
    
    # Risk parameters
    GREEKS_LIMITS = {
        "DELTA": 5000,
        "GAMMA": -2000,
        "VEGA": 30000
    }
    
    # Backtesting
    STRESS_SCENARIOS = [
        "2020-03",
        "2008-10",
        "2015-08"
    ]
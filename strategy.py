# strategy.py
import datetime
import numpy as np
from scipy.stats import norm

class AVWAPCalculator:
    """
    Calculates Anchored Volume-Weighted Average Price (AVWAP)
    from an anchor time using tick (price, volume) data.
    """
    def __init__(self, anchor_time):
        self.anchor_time = anchor_time  # e.g., "09:15"
        self.cumulative_price_volume = 0.0
        self.cumulative_volume = 0.0

    def update(self, price, volume):
        self.cumulative_price_volume += price * volume
        self.cumulative_volume += volume
        return self.get_avwap()

    def get_avwap(self):
        if self.cumulative_volume == 0:
            return None
        return self.cumulative_price_volume / self.cumulative_volume

def calculate_delta(option_type, S, K, T, r, sigma):
    """
    Calculate option delta using the Black-Scholes formula.
    option_type: 'call' or 'put'
    S: underlying price, K: strike, T: time to expiry in years, r: risk-free rate, sigma: volatility.
    Returns the absolute delta.
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option_type.lower() in ['call', 'ce']:
        delta = norm.cdf(d1)
    else:
        delta = norm.cdf(d1) - 1
    return abs(delta)

class Strategy:
    def __init__(self, trading_config):
        self.trading_config = trading_config
        self.avwap_straddle = AVWAPCalculator(self.trading_config["avwap_anchor_time"])
        self.avwap_call = AVWAPCalculator(self.trading_config["avwap_anchor_time"])
        self.avwap_put = AVWAPCalculator(self.trading_config["avwap_anchor_time"])

    def update_vwap(self, atm_call_price, atm_call_volume, atm_put_price, atm_put_volume):
        combined_price = atm_call_price + atm_put_price
        combined_volume = atm_call_volume + atm_put_volume
        avwap_straddle_value = self.avwap_straddle.update(combined_price, combined_volume)
        avwap_call_value = self.avwap_call.update(atm_call_price, atm_call_volume)
        avwap_put_value = self.avwap_put.update(atm_put_price, atm_put_volume)
        return avwap_straddle_value, avwap_call_value, avwap_put_value

    def check_entry_condition(self, atm_call_price, atm_put_price, avwap_straddle, avwap_call, avwap_put, prev_straddle=None):
        """
        Returns True if:
          - Combined ATM straddle price is below its AVWAP
          - Individual ATM call and put prices are below their respective AVWAPs.
        """
        current_straddle = atm_call_price + atm_put_price
        if current_straddle < avwap_straddle and atm_call_price < avwap_call and atm_put_price < avwap_put:
            return True
        else:
            return False

    def select_strikes(self, option_chain, underlying_price, expiry_datetime, sigma=0.2, r=0.03):
        """
        Selects the following strikes:
          - ATM strike: closest to underlying_price.
          - Short Call (approx. 4 delta) from call options with strike > ATM strike.
          - Long Call (approx. 2 delta) from call options with strike greater than short call.
          - Short Put (approx. 4 delta) from put options with strike < ATM strike.
          - Long Put (approx. 2 delta) from put options with strike less than short put.
        Option chain is assumed to be a list of dictionaries with keys: 'Strike', 'OptionType', 'LTP', 'ScripCode', etc.
        """
        strikes = sorted(list(set([opt['Strike'] for opt in option_chain])))
        atm_strike = min(strikes, key=lambda x: abs(x - underlying_price))
        # Get ATM call and put for reference:
        calls_atm = [opt for opt in option_chain if opt['OptionType'] == 'CE' and opt['Strike'] == atm_strike]
        puts_atm = [opt for opt in option_chain if opt['OptionType'] == 'PE' and opt['Strike'] == atm_strike]
        if not calls_atm or not puts_atm:
            raise Exception("ATM options not found in option chain.")
        atm_call = calls_atm[0]
        atm_put = puts_atm[0]
        T = (expiry_datetime - datetime.datetime.now()).total_seconds() / (365 * 24 * 3600)

        # Select short call (approx. 4 delta) from calls with strike > ATM
        candidate_calls = [opt for opt in option_chain if opt['OptionType'] == 'CE' and opt['Strike'] > atm_strike]
        selected_short_call = None
        selected_long_call = None
        min_diff = float("inf")
        for opt in candidate_calls:
            delta = calculate_delta("call", underlying_price, opt['Strike'], T, r, sigma)
            if abs(delta - 0.04) < min_diff:
                min_diff = abs(delta - 0.04)
                selected_short_call = opt
        if selected_short_call is None:
            raise Exception("Appropriate short call not found.")
        min_diff = float("inf")
        for opt in candidate_calls:
            if opt['Strike'] > selected_short_call['Strike']:
                delta = calculate_delta("call", underlying_price, opt['Strike'], T, r, sigma)
                if abs(delta - 0.02) < min_diff:
                    min_diff = abs(delta - 0.02)
                    selected_long_call = opt
        if selected_long_call is None:
            raise Exception("Appropriate long call not found.")

        # Select short put (approx. 4 delta) from puts with strike < ATM
        candidate_puts = [opt for opt in option_chain if opt['OptionType'] == 'PE' and opt['Strike'] < atm_strike]
        selected_short_put = None
        selected_long_put = None
        min_diff = float("inf")
        for opt in candidate_puts:
            delta = calculate_delta("put", underlying_price, opt['Strike'], T, r, sigma)
            if abs(delta - 0.04) < min_diff:
                min_diff = abs(delta - 0.04)
                selected_short_put = opt
        if selected_short_put is None:
            raise Exception("Appropriate short put not found.")
        min_diff = float("inf")
        for opt in candidate_puts:
            if opt['Strike'] < selected_short_put['Strike']:
                delta = calculate_delta("put", underlying_price, opt['Strike'], T, r, sigma)
                if abs(delta - 0.02) < min_diff:
                    min_diff = abs(delta - 0.02)
                    selected_long_put = opt
        if selected_long_put is None:
            raise Exception("Appropriate long put not found.")

        return {
            "atm_strike": atm_strike,
            "atm_call": atm_call,
            "atm_put": atm_put,
            "short_call": selected_short_call,
            "long_call": selected_long_call,
            "short_put": selected_short_put,
            "long_put": selected_long_put
        }

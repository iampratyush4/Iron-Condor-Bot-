class AdaptiveIronCondor:
    def __init__(self, volatility_surface, market_regime):
        self.vol_surface = volatility_surface
        self.regime = market_regime
    
    def determine_strikes(self, underlying_price, dte):
        # Adaptive delta based on volatility regime
        if self.regime.current() == "high":
            short_delta = 0.35
            long_delta = 0.15
        elif self.regime.current() == "low":
            short_delta = 0.25
            long_delta = 0.10
        else:  # medium
            short_delta = 0.30
            long_delta = 0.12
        
        # Calculate strikes
        atm_strike = self._nearest_strike(underlying_price)
        call_strikes = self._find_strikes('call', atm_strike, dte, short_delta, long_delta)
        put_strikes = self._find_strikes('put', atm_strike, dte, short_delta, long_delta)
        
        return {
            'short_call': call_strikes['short'],
            'long_call': call_strikes['long'],
            'short_put': put_strikes['short'],
            'long_put': put_strikes['long']
        }
    
    def _find_strikes(self, option_type, atm_strike, dte, short_delta, long_delta):
        # Find strikes based on volatility surface
        # This is simplified - real implementation would use the surface
        if option_type == 'call':
            short_strike = atm_strike * (1 + short_delta * 0.05)
            long_strike = atm_strike * (1 + long_delta * 0.08)
        else:
            short_strike = atm_strike * (1 - short_delta * 0.05)
            long_strike = atm_strike * (1 - long_delta * 0.08)
        
        return {
            'short': self._nearest_strike(short_strike),
            'long': self._nearest_strike(long_strike)
        }
    
    def _nearest_strike(self, price, step=50):
        return round(price / step) * step
class GammaScalper:
    def __init__(self, portfolio_manager):
        self.portfolio = portfolio_manager
    
    def adjust_for_gamma(self, current_delta):
        target_delta = self.portfolio.target_delta()
        gamma_exposure = self.portfolio.gamma_exposure()
        
        # Calculate required hedge
        delta_difference = current_delta - target_delta
        hedge_qty = delta_difference / gamma_exposure if gamma_exposure != 0 else 0
        
        if abs(hedge_qty) > 5:  # Minimum hedge size
            return {
                'symbol': 'NIFTY',
                'quantity': round(hedge_qty),
                'side': 'SELL' if hedge_qty > 0 else 'BUY'
            }
        return None
import pandas as pd
from scipy.stats import norm

class StressTester:
    def __init__(self, portfolio):
        self.portfolio = portfolio
    
    def historical_scenario(self, period):
        # Load historical scenario data
        scenario = pd.read_csv(f"scenarios/{period}.csv")
        pnl_impact = 0
        
        for _, row in scenario.iterrows():
            for position in self.portfolio:
                if position['symbol'] == row['symbol']:
                    pnl_impact += position['qty'] * (
                        row['close'] - position['entry_price']
                    )
        return pnl_impact
    
    def monte_carlo_var(self, iterations=10000, confidence=0.99):
        returns = self._simulate_returns()
        losses = [-x for x in returns if x < 0]
        losses.sort()
        var_index = int(len(losses) * (1 - confidence))
        return losses[var_index] if losses else 0
    
    def _simulate_returns(self, days=1):
        # Simplified implementation
        # In practice, use correlated asset returns with Cholesky decomposition
        return [norm.rvs(loc=0, scale=0.02) for _ in range(10000)]
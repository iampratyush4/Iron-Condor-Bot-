import numpy as np
from scipy.stats import norm

class MonteCarloBacktester:
    def __init__(self, strategy, n_simulations=1000):
        self.strategy = strategy
        self.n_simulations = n_simulations

    def run(self, initial_capital, periods=252):
        results = []
        for _ in range(self.n_simulations):
            capital = initial_capital
            for _ in range(periods):
                # Simulate market conditions
                market_return = norm.rvs(loc=0.0003, scale=0.015)
                volatility_change = norm.rvs(loc=0, scale=0.05)

                # Update strategy parameters (fixed missing “)” below)
                self.strategy.update_volatility(
                    self.strategy.volatility * (1 + volatility_change)
                )

                # Execute strategy
                pnl = self.strategy.execute(market_return)
                capital = capital * (1 + pnl)

            results.append(capital)

        # Calculate risk metrics
        returns = np.log(np.array(results) / initial_capital)
        mean_return = np.mean(returns)
        volatility = np.std(returns)
        sharpe = mean_return / volatility if volatility != 0 else 0

        # Calculate VaR and CVaR
        sorted_returns = np.sort(returns)
        var_95 = sorted_returns[int(0.05 * len(sorted_returns))]
        cvar_95 = np.mean(sorted_returns[:int(0.05 * len(sorted_returns))])

        return {
            'final_capital': results,
            'mean_return'  : mean_return,
            'volatility'   : volatility,
            'sharpe'       : sharpe,
            'var_95'       : var_95,
            'cvar_95'      : cvar_95
        }

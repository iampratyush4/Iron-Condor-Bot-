import numpy as np
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self, strategies, correlation_matrix):
        self.strategies = strategies
        self.corr_matrix = correlation_matrix
    
    def mean_cvar_optimization(self, target_return=0.15):
        # Calculate expected returns and covariances
        returns = np.array([s.expected_return for s in self.strategies])
        cov_matrix = self._covariance_from_correlation()
        
        # Optimization function
        def cvar_objective(weights, alpha=0.95):
            portfolio_return = np.dot(weights, returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -portfolio_return + 2.5 * portfolio_vol  # Simplified CVAR
        
        # Constraints
        constraints = (
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Sum to 1
            {'type': 'eq', 'fun': lambda w: np.dot(w, returns) - target_return}
        )
        
        # Bounds
        bounds = [(0, 0.25) for _ in range(len(self.strategies))]  # Max 25% per strategy
        
        # Initial guess
        init_weights = np.ones(len(self.strategies)) / len(self.strategies)
        
        # Optimization
        result = minimize(
            cvar_objective, 
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return result.x
    
    def _covariance_from_correlation(self, base_vol=0.20):
        # Create covariance matrix from correlation
        # Using base volatility for all strategies
        vols = np.ones(len(self.strategies)) * base_vol
        cov = np.diag(vols) @ self.corr_matrix @ np.diag(vols)
        return cov
from py_vollib_vectorized import vectorized
import pandas as pd

class GreeksCalculator:
    def __init__(self, risk_free_rate=0.03):
        self.r = risk_free_rate
    
    def calculate_all_greeks(self, positions):
        results = []
        for pos in positions:
            greeks = vectorized.greeks(
                'c' if pos['option_type'] == 'call' else 'p',
                pos['underlying_price'],
                pos['strike'],
                pos['t'],
                self.r,
                pos['iv'],
                return_as='dict'
            )
            results.append({
                'symbol': pos['symbol'],
                'delta': greeks['delta'] * pos['qty'],
                'gamma': greeks['gamma'] * pos['qty'],
                'theta': greeks['theta'] * pos['qty'],
                'vega': greeks['vega'] * pos['qty']
            })
        return pd.DataFrame(results)
    
    def portfolio_greeks(self, positions):
        df = self.calculate_all_greeks(positions)
        return df.sum().to_dict()
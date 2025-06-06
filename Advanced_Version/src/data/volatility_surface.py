import numpy as np
from scipy.interpolate import griddata

class VolatilitySurface:
    def __init__(self, option_chain):
        self.surface = self._build_surface(option_chain)
    
    def _build_surface(self, chain):
        # Extract necessary data
        strikes = np.array([opt['Strike'] for opt in chain])
        expiries = np.array([opt['DaysToExpiry'] for opt in chain])
        ivs = np.array([opt['ImpliedVol'] for opt in chain])
        
        # Create grid for interpolation
        grid_x, grid_y = np.mgrid[
            min(strikes):max(strikes):100j,
            min(expiries):max(expiries):100j
        ]
        
        # Interpolate volatility surface
        return griddata(
            (strikes, expiries), ivs, (grid_x, grid_y), method='cubic'
        )
    
    def get_volatility(self, strike, dte):
        # Nearest neighbor lookup on grid
        x_idx = np.abs(self.surface.x - strike).argmin()
        y_idx = np.abs(self.surface.y - dte).argmin()
        return self.surface.z[x_idx, y_idx]
    
    def calculate_skew(self, atm_strike, dte):
        # Calculate 10-delta skew
        k_90 = atm_strike * 0.9
        k_110 = atm_strike * 1.1
        vol_90 = self.get_volatility(k_90, dte)
        vol_110 = self.get_volatility(k_110, dte)
        return vol_90 - vol_110
import panel as pn
import hvplot.pandas

class RiskDashboard:
    def __init__(self, portfolio_manager):
        self.pm = portfolio_manager
        pn.extension()
    
    def create_dashboard(self):
        # Create components
        greeks_pane = self._create_greeks_pane()
        exposure_chart = self._create_exposure_chart()
        risk_metrics = self._create_risk_metrics()
        performance_plot = self._create_performance_plot()
        
        # Layout
        dashboard = pn.Column(
            pn.Row(greeks_pane, risk_metrics),
            pn.Row(exposure_chart, performance_plot),
            sizing_mode='stretch_width'
        )
        return dashboard
    
    def _create_greeks_pane(self):
        greeks = self.pm.current_greeks()
        return pn.WidgetBox(
            pn.indicators.Gauge(
                name='Delta', value=greeks['delta'], 
                bounds=(self.pm.config.DELTA_LIMITS[0], self.pm.config.DELTA_LIMITS[1])
            ),
            pn.indicators.Gauge(
                name='Gamma', value=greeks['gamma'], 
                bounds=(self.pm.config.GAMMA_LIMITS[0], self.pm.config.GAMMA_LIMITS[1])
            ),
            pn.indicators.Gauge(
                name='Vega', value=greeks['vega'], 
                bounds=(self.pm.config.VEGA_LIMITS[0], self.pm.config.VEGA_LIMITS[1])
            )
        )
    
    def _create_exposure_chart(self):
        exposure = self.pm.get_exposure_report()
        return exposure.hvplot.bar(
            x='asset', y='exposure', title='Portfolio Exposure'
        )
    
    def _create_risk_metrics(self):
        var = self.pm.value_at_risk(confidence=0.95)
        cvar = self.pm.conditional_var(confidence=0.95)
        return pn.indicators.Number(
            name='CVaR 95%', value=cvar,
            format='${value:,.0f}',
            colors=[(0.3, 'green'), (0.8, 'gold'), (1, 'red')]
        )
    
    def _create_performance_plot(self):
        performance = self.pm.get_performance_history()
        return performance.hvplot.line(
            x='date', y='equity', title='Performance'
        )
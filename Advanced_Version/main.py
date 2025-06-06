from src.data.data_fetcher import EnhancedDataFetcher
from src.execution.order_executor import SmartOrderExecutor
from src.risk.risk_manager import InstitutionalRiskManager
from src.strategy.core_strategy import AdaptiveIronCondor
from src.portfolio.optimizer import PortfolioOptimizer
from src.utils.dashboard import RiskDashboard
import time

class HedgeFundTradingSystem:
    def __init__(self, config):
        self.config = config
        self.data_fetcher = EnhancedDataFetcher(config)
        self.order_executor = SmartOrderExecutor(config)
        self.risk_manager = InstitutionalRiskManager(config)
        self.portfolio = PortfolioManager(config)
        self.strategy = AdaptiveIronCondor(config)
        self.dashboard = RiskDashboard(self.portfolio)
    
    def run(self):
        # Initialize
        self.data_fetcher.connect()
        self.dashboard.start()
        
        # Main loop
        while True:
            try:
                # Market data update
                market_data = self.data_fetcher.get_full_market_state()
                
                # Risk check
                if not self.risk_manager.approve_trading():
                    time.sleep(60)
                    continue
                
                # Generate trades
                trades = self.strategy.generate_trades(market_data)
                
                # Execute
                for trade in trades:
                    execution_plan = self.order_executor.route_order(trade)
                    self.order_executor.execute(execution_plan)
                
                # Portfolio rebalance
                if self.portfolio.needs_rebalance():
                    rebalance_orders = self.portfolio.create_rebalance_plan()
                    self.order_executor.execute_batch(rebalance_orders)
                
                # Update dashboard
                self.dashboard.update()
                
                time.sleep(30)
                
            except Exception as e:
                self.handle_error(e)
    
    def handle_error(self, exception):
        # Sophisticated error handling
        self.risk_manager.emergency_protocol()
        self.order_executor.cancel_all_orders()
        # Alerting and logging
        time.sleep(300)  # Cool-off period

if __name__ == "__main__":
    config = load_config()  # Implement config loading
    system = HedgeFundTradingSystem(config)
    system.run()
# risk_manager.py
import config

class RiskManager:
    def __init__(self, trading_config, logger):
        self.trading_config = trading_config
        self.logger = logger
        self.current_pnl = 0.0

    def update_pnl(self, current_pnl):
        """
        Update the current mark-to-market P&L.
        """
        self.current_pnl = current_pnl
        return self.current_pnl

    def check_risk(self):
        """
        Checks if current P&L has breached stop-loss or profit target.
        Returns 'stop_loss', 'target', or None.
        """
        if self.current_pnl <= - (self.trading_config["capital"] * self.trading_config["stop_loss_pct"] / 100):
            self.logger.log_event("RISK_TRIGGER", f"Stop-loss reached: PnL {self.current_pnl}")
            return "stop_loss"
        if self.current_pnl >= (self.trading_config["capital"] * self.trading_config["target_pct"] / 100):
            self.logger.log_event("RISK_TRIGGER", f"Profit target reached: PnL {self.current_pnl}")
            return "target"
        return None

    def should_exit_based_on_avwap(self, current_straddle, avwap_straddle, previous_straddle=None):
        """
        Checks if the current ATM straddle price has crossed above its AVWAP.
        """
        if previous_straddle is not None:
            if previous_straddle < avwap_straddle and current_straddle >= avwap_straddle:
                self.logger.log_event("EXIT_SIGNAL", f"Straddle crossed above AVWAP: {current_straddle} vs {avwap_straddle}")
                return True
        else:
            if current_straddle >= avwap_straddle:
                self.logger.log_event("EXIT_SIGNAL", f"Straddle above AVWAP: {current_straddle} vs {avwap_straddle}")
                return True
        return False

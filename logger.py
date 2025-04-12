# logger.py
import csv
import os
from datetime import datetime

class CSVLogger:
    def __init__(self, log_file, dashboard_file):
        self.log_file = log_file
        self.dashboard_file = dashboard_file
        # Create log file if it does not exist.
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "EventType", "Details", "OrderID"])
        # Create dashboard file if it does not exist.
        if not os.path.exists(self.dashboard_file):
            with open(self.dashboard_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Status", "PnL", "TradeDetails"])

    def log_event(self, event_type, details, order_id=""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, event_type, details, order_id]
        with open(self.log_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        print(f"[{timestamp}] {event_type}: {details} {order_id}")

    def update_dashboard(self, status, pnl, trade_details=""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, status, pnl, trade_details]
        # Overwrite the dashboard file
        with open(self.dashboard_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Status", "PnL", "TradeDetails"])
            writer.writerow(row)

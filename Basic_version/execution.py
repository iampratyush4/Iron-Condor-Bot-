# execution.py
import time
import config

class OrderExecutor:
    def __init__(self, client, trading_config, logger):
        self.client = client  # Instance of FivePaisaClient from data_fetcher
        self.trading_config = trading_config
        self.logger = logger

    def place_order(self, order_details, retry=0):
        """
        Places an order using the 5paisa API and returns the order ID if successful.
        Retries on failure up to max_retries.
        """
        try:
            response = self.client.place_order(order_details)
            if response.get("status") == "success":
                order_id = response.get("order_id")
                self.logger.log_event("ORDER_PLACED", f"{order_details}", order_id=order_id)
                return order_id
            else:
                self.logger.log_event("ORDER_FAILED", f"{order_details} Error: {response}", order_id="")
                if retry < self.trading_config["max_retries"]:
                    time.sleep(1)
                    return self.place_order(order_details, retry + 1)
                else:
                    raise Exception(f"Order failed after retries: {order_details}")
        except Exception as e:
            self.logger.log_event("ORDER_EXCEPTION", f"{order_details} Exception: {str(e)}", order_id="")
            if retry < self.trading_config["max_retries"]:
                time.sleep(1)
                return self.place_order(order_details, retry + 1)
            else:
                raise e

    def execute_iron_condor(self, trade_setup):
        """
        Places the four orders for the Iron Condor:
          1. Buy long call (hedge)
          2. Buy long put (hedge)
          3. Sell short call
          4. Sell short put
        Returns a dict of order IDs.
        """
        order_ids = {}
        # Place hedge orders first (buy orders)
        for leg in ["long_call", "long_put"]:
            order_details = {
                "ScripCode": trade_setup[leg]['ScripCode'],
                "OrderType": "Buy",
                "PriceType": "MKT",
                "Qty": self.trading_config["lot_size"] * self.trading_config["num_lots"],
                "ProductType": "CNC",
                "Exchange": "N"
            }
            order_id = self.place_order(order_details)
            order_ids[leg] = order_id

        # Then place short orders (sell orders)
        for leg in ["short_call", "short_put"]:
            order_details = {
                "ScripCode": trade_setup[leg]['ScripCode'],
                "OrderType": "Sell",
                "PriceType": "MKT",
                "Qty": self.trading_config["lot_size"] * self.trading_config["num_lots"],
                "ProductType": "CNC",
                "Exchange": "N"
            }
            order_id = self.place_order(order_details)
            order_ids[leg] = order_id

        self.logger.log_event("ENTRY_DONE", f"Iron Condor placed with orders: {order_ids}")
        return order_ids

    def exit_position(self, trade_setup):
        """
        Exits the Iron Condor by reversing the orders:
           - For short legs (sell), place buy orders.
           - For long legs (buy), place sell orders.
        Returns a dict of order IDs.
        """
        order_ids = {}
        # Close short positions first (buy to cover)
        for leg in ["short_call", "short_put"]:
            order_details = {
                "ScripCode": trade_setup[leg]['ScripCode'],
                "OrderType": "Buy",
                "PriceType": "MKT",
                "Qty": self.trading_config["lot_size"] * self.trading_config["num_lots"],
                "ProductType": "CNC",
                "Exchange": "N"
            }
            order_id = self.place_order(order_details)
            order_ids[leg] = order_id

        # Close long positions (sell to exit)
        for leg in ["long_call", "long_put"]:
            order_details = {
                "ScripCode": trade_setup[leg]['ScripCode'],
                "OrderType": "Sell",
                "PriceType": "MKT",
                "Qty": self.trading_config["lot_size"] * self.trading_config["num_lots"],
                "ProductType": "CNC",
                "Exchange": "N"
            }
            order_id = self.place_order(order_details)
            order_ids[leg] = order_id

        self.logger.log_event("EXIT_DONE", f"Exited Iron Condor with orders: {order_ids}")
        return order_ids

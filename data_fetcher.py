# data_fetcher.py
import datetime
import config
# Ensure you have installed the 5paisa SDK from https://github.com/OpenApi-5p/py5paisa
from py5paisa import FivePaisaClient

class DataFetcher:
    def __init__(self, api_config):
        """
        Initialize the FivePaisaClient using TOTP-based authentication.
        """
        # Build the credentials dictionary required by the 5paisa SDK
        cred = config.Cred
        # Instantiate the 5paisa client with credentials.
        self.client = FivePaisaClient(cred=cred)
        # Perform TOTP-based authentication.
        TOTP= input("Enter TOTP:")
        self.client.get_totp_session(
            api_config.get("CLIENT_CODE", "YourClientCode"),
            TOTP,
            api_config.get("PIN", "YourPin"),
        )

        self.latest_option_chain = None
        self.latest_expiry = None
        self.underlying_price = None

    def get_latest_monthly_expiry(self):
        """
        Fetch available BankNifty expiries and select the monthly expiry
        (assumed to be the last Thursday of the current month that is >= today).
        """
        expiries = self.client.get_expiry("N", "BANKNIFTY")  # returns list of expiry strings
        today = datetime.date.today()
        monthly_expiry = None
        for exp_str in expiries:
            try:
                exp_date = datetime.datetime.strptime(exp_str, "%d-%b-%Y").date()
            except Exception:
                continue
            if exp_date.month == today.month and exp_date >= today:
                if monthly_expiry is None or exp_date > monthly_expiry:
                    monthly_expiry = exp_date
        self.latest_expiry = monthly_expiry
        return monthly_expiry

    def get_option_chain(self):
        """
        Retrieves the full option chain for BankNifty for the latest expiry.
        """
        if self.latest_expiry is None:
            self.get_latest_monthly_expiry()
        if self.latest_expiry is None:
            raise Exception("No valid monthly expiry found.")

        chain = self.client.get_option_chain("N", "BANKNIFTY", self.latest_expiry.strftime("%d-%b-%Y"))
        self.latest_option_chain = chain
        return chain

    def get_underlying_price(self):
        """
        Retrieves the current BankNifty underlying price (LTP).
        """
        quote = self.client.get_quote("N", "BANKNIFTY")
        self.underlying_price = float(quote.get("LTP", 0))
        return self.underlying_price

    def subscribe_tick_data(self, instruments, callback):
        """
        Subscribes to tick data for the list of instrument ScripCodes.
        The callback is a function that receives tick data as a parameter.
        """
        self.client.subscribe_ticks(instruments, callback)

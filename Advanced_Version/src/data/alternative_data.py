import requests
import pandas as pd

class AlternativeData:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def fetch_options_flow(self):
        url = f"https://api.optionsflow.io/v2/signals?apikey={self.api_key}"
        response = requests.get(url)
        return pd.DataFrame(response.json()['signals'])
    
    def detect_block_trades(self, min_size=1000000):
        flow = self.fetch_options_flow()
        return flow[flow['size'] >= min_size]
    
    def get_economic_indicators(self):
        url = f"https://api.econdata.com/indicators?apikey={self.api_key}"
        return requests.get(url).json()
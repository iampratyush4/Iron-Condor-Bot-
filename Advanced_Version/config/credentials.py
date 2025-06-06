import os

class Credentials:
    @property
    def FIVEPAISA(self):
        return {
            "CLIENT_CODE": os.getenv("FP_CLIENT_CODE"),
            "TOTP_SECRET": os.getenv("FP_TOTP_SECRET"),
            "PIN": os.getenv("FP_PIN"),
            "API_KEY": os.getenv("FP_API_KEY"),
            "API_SECRET": os.getenv("FP_API_SECRET")
        }
    
    @property
    def ALTERNATIVE_DATA_SOURCES(self):
        return {
            "OPTIONS_FLOW": os.getenv("OPTIONS_FLOW_API"),
            "ECON_DATA": os.getenv("ECON_DATA_API")
        }
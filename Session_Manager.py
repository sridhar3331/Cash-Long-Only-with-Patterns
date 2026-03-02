# Importing Libraries
from py5paisa import FivePaisaClient

import os
working_dir = os.chdir(r"D:\ALGO TRADING\LIVE\ZERODHA CASH")


import pyotp
import credent as mahaauth 


_client = None


def get_session():
    global _client
    if _client is None:
        print("🔐 Logging in...")
        
        # 5 Paisa Login
        _client = FivePaisaClient(cred=mahaauth.cred)
        # New TOTP based authentication
        _client.get_totp_session(mahaauth.client_id,pyotp.TOTP(mahaauth.token).now(),mahaauth.pin)
        
    return _client





import os
working_dir = os.chdir(r"D:\ALGO TRADING\LIVE\ZERODHA CASH")


##### Importing Session From Session_Manager ####
from Session_Manager import get_session
#################################################

##### Importing From User Input Library ######
from User_Input import Tickers,instrument_df
##############################################

##### Importing From Common Function Library ######
from Common_Functions import instrument_lookup
###################################################


import datetime as dt
import pytz
UTC = pytz.timezone('Asia/Kolkata')
import time
import threading
import json





_client = get_session()



# Initialize spot prices and last update time
spot_prices = {ticker: None for ticker in Tickers}
last_update_time = {ticker: dt.datetime.now(UTC) for ticker in Tickers}

# Define the callback function for incoming data
def on_message(ws, message):
    global spot_prices, last_update_time
    data = json.loads(message)

    if data:
        ticker_symbol = instrument_df[instrument_df['ScripCode'] == data[0]['Token']]['Name'].iloc[0]
        last_rate = data[0]['LastRate']
        spot_prices[ticker_symbol] = last_rate
        last_update_time[ticker_symbol] = dt.datetime.now(UTC)


# Subscribe to data feed
def subscribe_data():
    global client
    req_list = [
        {"Exch": "N", "ExchType": "C", "ScripCode": str(instrument_lookup(symbol=ticker))}
        for ticker in Tickers
    ]
    req_data = _client.Request_Feed('mf', 's', req_list)
    _client.connect(req_data)
    _client.receive_data(on_message)


# Restart WebSocket streaming without restarting program
def restart_streaming(reason):
    current_time = dt.datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{current_time} - Restarting WebSocket due to: {reason}\n"
    
    print(f"{current_time} - Restarting WebSocket due to: {reason}\n")

    with open("restart_log.txt", "a") as log_file:
        log_file.write(log_message)

    print(log_message)

    try:
        _client.close_connection()   # <-- Gracefully close old WebSocket
    except Exception as e:
        print(f"Error closing old connection: {e}")

    # Small delay before reconnecting
    time.sleep(2)

    # Start a new streaming thread
    new_stream = threading.Thread(target=subscribe_data)
    new_stream.daemon = True
    new_stream.start()


# Function to check for stale data
def check_stale_data():
    global last_update_time
    current_time = dt.datetime.now(UTC)
    for ticker, last_time in last_update_time.items():
        if (current_time - last_time).total_seconds() > 300:  # 5 minutes
            restart_streaming(f"Ticker {ticker} not updated in last 5 minutes.")
            time.sleep(120)
            break  # Restart once; don’t trigger multiple restarts


# Start monitoring stale data in a separate thread
def monitor_data():
    while True:
        check_stale_data()
        time.sleep(60)  # Check every minute
        
# Stop Connection        
def stop_streaming():
    
    try:
        _client.close_connection()   # <-- Gracefully close old WebSocket
    except Exception as e:
        print(f"Error closing old connection: {e}")

        
        
        

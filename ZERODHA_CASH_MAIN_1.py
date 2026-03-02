import os
working_dir = os.chdir(r"D:\ALGO TRADING\LIVE\ZERODHA CASH")
import requests

import sys
import pytz
UTC = pytz.timezone('Asia/Kolkata')
import datetime as dt
import time
import threading


# Downloading Script Master
def download_csv_from_url(url, local_filename):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Save the response content to the local CSV file
            with open(local_filename, 'wb') as csv_file:
                csv_file.write(response.content)
            print(f"CSV file downloaded and saved as {local_filename}")
        else:
            print(f"Failed to download CSV file. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage:
url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"

local_filename = "scripmaster.csv"


download_csv_from_url(url, local_filename)




##### Importing From User Input Library ######
from User_Input import START_TIME,EXIT_TIME 
##############################################


##### Importing Common Functions #############
from Common_Functions import data_list,getting_ohlc
##############################################


##### Importing Streaming Data #####################################
from Streaming_Ltp import subscribe_data,monitor_data,stop_streaming 
 ####################################################################


###### Importing OHLC ##########
from ohlc import ohlc_update
################################

###### Importing Cash Trade Algo #######################
from Cash_Trade_Long_Only import Cash_Trade_Long_Only
########################################################

####### Importing Bear Call Algo ##########################
#from Bear_Call_For_Cash_Long import Cash_Bear_Call_Spread
###########################################################




if __name__ == "__main__":
    IST = pytz.timezone('Asia/Kolkata')
    now = dt.datetime.now(IST)
    closetime = now.replace(hour=START_TIME[0], minute=START_TIME[1], second=START_TIME[2])
    endTime = now.replace(hour=EXIT_TIME[0], minute=EXIT_TIME[1], second=EXIT_TIME[2])

    interval = (closetime - now).total_seconds()
    if interval > 0:
        print(f'⏳ Algo will start in {interval:.2f} seconds')
        time.sleep(interval)

    print('🚀 Algo Starting Now!!!')
    
    
    getting_ohlc()
    
    time.sleep(10)
    
    # Start all daemon threads
    threads = [
        threading.Thread(target=subscribe_data, daemon=True),
        threading.Thread(target=monitor_data, daemon=True),
        threading.Thread(target=ohlc_update, daemon=True),
        threading.Thread(target=Cash_Trade_Long_Only, daemon=True)         
    ]

    for t in threads:
        time.sleep(15)
        t.start()
        

    # Run until EXIT_TIME
    while dt.datetime.now(IST) < endTime:
        print("✅ Algo running...")
        time.sleep(300)

    print("🛑 Exit time reached. Shutting down...")

    # Stop streaming and exit
    stop_streaming()
    time.sleep(2)
    sys.exit(0)

 


'''
# Start all daemon threads
threads = [
    threading.Thread(target=subscribe_data, daemon=True),
    threading.Thread(target=monitor_data, daemon=True),
    threading.Thread(target=ohlc_update, daemon=True),
    threading.Thread(target=Cash_Trade_Long_Only, daemon=True),  
    threading.Thread(target=Cash_Bear_Call_Spread, daemon=True)  
]

'''





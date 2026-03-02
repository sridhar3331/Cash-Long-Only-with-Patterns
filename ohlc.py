# Importing Libraries
import os
working_dir = os.chdir(r"D:\ALGO TRADING\LIVE\ZERODHA CASH")

##### Importing Common Variables #############
from User_Input import EXIT_TIME
##############################################


##### Importing Common Functions #############
from Common_Functions import is_required_time,getting_ohlc,data_list
##############################################

import time
import datetime as dt
import pytz
UTC = pytz.timezone('Asia/Kolkata')



def ohlc_update():
    endTime = dt.datetime.now(pytz.timezone('Asia/Kolkata')).replace(hour=EXIT_TIME[0], minute=EXIT_TIME[1],second=EXIT_TIME[2])
    last_updated_minute = None

    while dt.datetime.now(pytz.timezone('Asia/Kolkata')) < endTime:
        try:
            now = dt.datetime.now(pytz.timezone("Asia/Kolkata"))
            #print("🕒 Checking at:", now.strftime("%H:%M:%S"))

            if is_required_time():
                if last_updated_minute != now.minute:
                    print("✅ is_required_time() matched. Calling getting_ohlc()...")
                    getting_ohlc()
                    last_updated_minute = now.minute
                else:
                    print("⚠️ Skipping duplicate call in same minute.")
            # else:
            #     print("⏭ Not required time, skipping.")

        except Exception as e:
            print("Error:", e)

        time.sleep(1)

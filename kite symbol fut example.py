# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 17:00:57 2025

@author: user
"""
import os
working_dir = os.chdir(r"D:\ALGO TRADING\LIVE\ZERODHA CASH")
import datetime as dt
from pyotp import TOTP
from kiteconnect import KiteConnect
import sridharzerodhacred
import urllib
from selenium import webdriver
import pandas as pd
import time

# Declaring Login Credentials in a variable
api_key = sridharzerodhacred.apikey
key_secret = sridharzerodhacred.api_secret
userID = sridharzerodhacred.userid
pwd = sridharzerodhacred.password
totp_key = sridharzerodhacred.totp



# Using Selenium Web driver to get login url
browser = webdriver.Chrome()
browser.get("https://kite.zerodha.com/connect/login?v=3&api_key="+urllib.parse.quote_plus(api_key))
browser.implicitly_wait(5)


# Detecting User Name and Password field in a browser
username = browser.find_element("xpath", '/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
password = browser.find_element("xpath", '/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input') 

# Sending user name and password to the field in the browser
username.send_keys(userID)
password.send_keys(pwd)

#Checkbox finding
browser.find_element("xpath", '/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/div/label/span[1]').click()

# Click Login Button finding
browser.find_element("xpath", '/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
time.sleep(2)


#Provide OTP programatically
pin = browser.find_element("xpath", '/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/form/div[1]/input')
totp = TOTP(totp_key)
token = totp.now()
pin.send_keys(token)

#Click button and Get Token
#browser.find_element("xpath", '/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/form/div[2]/button').click()
time.sleep(1)


temp_token=browser.current_url.split('request_token=')[1][:32]
# Save in Database or text File
print('temp_token', temp_token)

#Generate Session

kite = KiteConnect(api_key=api_key)

data = kite.generate_session(temp_token, api_secret=key_secret)
kite.set_access_token(data["access_token"])
browser.close()

# Getting Instrument for 5 paisa
instrument_df = pd.read_csv('scripmaster.csv')
#instrument_df = instrument_df[(instrument_df.Exch == 'N')&(instrument_df.CpType == 'XX')]
instrument_df = instrument_df[(instrument_df.Exch == 'N')]

# Getting Instrument for Zerodha
nse_futdump = kite.instruments("NFO")
nse_fut = pd.DataFrame(nse_futdump)
nse_fut = nse_fut[nse_fut.instrument_type=='FUT']


# Getting Script Code
def instrument_lookup(instrument=instrument_df, symbol='TCS 26 DEC 2024'):
    ## This function is used to find the instrument token number
    try:
        return instrument[instrument.Name == symbol].ScripCode.values[0]
    except:
        return -1
    
    

# Finding Future Contract
def Future(ticker):

    """
    Get the future contract name for a given ticker with expiry >= 4 days from today.

    Parameters:
    - ticker (str): The symbol root of the desired contract.

    Returns:
    - str: The name of the future contract (e.g., 'TICKER DD MMM YYYY').
    """
    global instrument_df  # Assuming `instrument_df` is defined globally

    # Filter rows for the given ticker
    contracts = instrument_df[(instrument_df.SymbolRoot == ticker)&(instrument_df.ScripType == 'XX')&(instrument_df.Series == 'XX')]

    # Parse expiry dates
    contracts['Expiry'] = pd.to_datetime(contracts['Expiry'])

    # Get today's date
    today = dt.datetime.today()

    # Filter contracts with expiry >= 4 days from today
    valid_contracts = contracts[contracts['Expiry'] >= today + dt.timedelta(days=5)]

    # Check if any valid contract exists
    if valid_contracts.empty:
        raise ValueError(f"No valid contracts found for ticker {ticker} with expiry >= 4 days.")

    # Get the earliest valid contract
    next_contract = valid_contracts.sort_values(by='Expiry').iloc[0]

    return next_contract['Name']

#Future('BANKNIFTY')

# Kite Future Symbol Lookup
def kite_fut(symbol):
    if symbol == 'NIFTY 50':
        symbol = 'NIFTY'
    if symbol == 'NIFTY BANK':
        symbol = 'BANKNIFTY'
    
    dates = nse_fut[(nse_fut.name == symbol)]
    dates = dates['expiry'].unique().tolist()
    dates = [str(date) for date in dates]
    
    dates = [dt.datetime.strptime(date, '%Y-%m-%d') for date in dates]
    
    today=dt.datetime.today()
    dates.sort()
    next_date = min(date for date in dates if date > today)
    if (next_date - today).days >= 10:
        trade = next_date
    else:
        trade = dates[1]
    ff=trade.strftime('%y%b').upper()
    return symbol+ff+'FUT'    

#kite_fut("BANKNIFTY")        
instrument_lookup(instrument=instrument_df, symbol='BANKNIFTY 28 OCT 2025')    

# kite symbol only for future
def Kite_Symbol(sym):
    
    code = instrument_lookup(instrument=instrument_df, symbol=sym)
    
    kite_sym = nse_fut[nse_fut.exchange_token == str(code)].tradingsymbol.values[0]
    
    return kite_sym


Kite_Symbol('BANKNIFTY 25 NOV 2025')


type(nse_fut['exchange_token'].iloc[-1])


kite.place_order(variety ='regular', exchange='NFO', tradingsymbol= 'BANKNIFTY25OCTFUT', transaction_type='BUY', quantity=35, product='NRML', order_type='MARKET')
kite.place_order(variety ='regular', exchange='NFO', tradingsymbol=fut, transaction_type='BUY', quantity=qty, product='NRML', order_type='MARKET')

kite.trades()

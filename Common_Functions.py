import os
working_dir = os.chdir(r"D:\ALGO TRADING\LIVE\ZERODHA CASH")

##### Importing From User Input Library ######
from User_Input import HEDGE_DELTA,SPREAD_DELTA,Tickers,instrument_df
##############################################

##### Importing Session From Session_Manager ####
from Session_Manager import get_session
#################################################


import datetime as dt
import pandas as pd
import pandas_ta as indi
import pytz
UTC = pytz.timezone('Asia/Kolkata')
import mibian as mb
import warnings
# Suppress future warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


data_list = {}


# Getting Script Code
def instrument_lookup(instrument=instrument_df, symbol='TCS 26 DEC 2024'):
    ## This function is used to find the instrument token number
    try:
        return instrument[instrument.Name == symbol].ScripCode.values[0]
    except:
        return -1
    
# Get OHLC Candles
def get_cash_market_data(symbol,timeframe):
    
    _client = get_session()
            
    scriptcode = instrument_lookup(instrument_df,symbol)
    
    #df=pd.DataFrame(client.historical_data(Exch='N', ExchangeSegment='C', ScripCode=scriptcode, time=timeframe, From=dt.date.today()-dt.timedelta(180), To=dt.date.today()-dt.timedelta(150)))
    
    df=pd.DataFrame(_client.historical_data(Exch='N', ExchangeSegment='C', ScripCode=scriptcode, time=timeframe, From=dt.date.today()-dt.timedelta(60), To=dt.date.today()))
    
    df.set_index("Datetime",inplace=True) 
        
    heikenashi = indi.ha(open_=df.iloc[:, df.columns.get_loc("Open")], high=df.iloc[:, df.columns.get_loc("High")], low=df.iloc[:, df.columns.get_loc("Low")], close=df.iloc[:, df.columns.get_loc("Close")])
    
    #heikenashi=indi.candles.ha(open_=df.Open,high=df.High,low=df.Low,close=df.Close)

    #print(heikenashi)
    df['HAOpen']=heikenashi["HA_open"]
    df['HAHigh']=heikenashi["HA_high"]
    df['HALow']=heikenashi["HA_low"]
    df['HAClose']=heikenashi["HA_close"]
    
    return df    
  

#get_cash_market_data("INFY","30m")  

# Function to find the next expiry date
def opt_exp(ticker):
    # Filter the relevant data for the given ticker and options
    dates = instrument_df[(instrument_df.SymbolRoot == ticker) & ((instrument_df.ScripType == 'CE') | (instrument_df.ScripType == 'PE'))]
    
    # Get the unique expiry dates and convert them to datetime objects
    dates = dates['Expiry'].unique().tolist()
    dates = [dt.datetime.strptime(date, '%Y-%m-%d') for date in dates]

    # Get today's date
    today = dt.datetime.today()

    # Sort the dates in ascending order
    dates.sort()
    
    # Adjust time to 15:30 for all dates in expiryList
    future_dates = [date.replace(hour=15, minute=30) for date in dates]

    # Find the next available date after today (skip today's date)
    future_dates = [date for date in dates if date > today]

    if future_dates:
        # Get the next available future date
        trade = future_dates[0]
    else:
        # If no future date is found, return None or handle the fallback
        return "No future expiry dates available."

    # Return the selected expiry date in the desired format
    return trade.strftime('%d %b %Y')
   
    
opt_exp('NIFTY')
opt_exp('BANKNIFTY')
opt_exp('INFY')

# Function to extract timestamp and convert it to a readable format
def process_expiry_date(date_str):
    # Extract the timestamp from the '/Date(...)' format
    timestamp = int(date_str.split('(')[1].split('+')[0])
    
    # Convert the timestamp to a datetime object
    date = dt.datetime.utcfromtimestamp(timestamp / 1000.0)
    
    # Convert datetime to the required format
    formatted_date = date.strftime('%d %b %Y')
    
    return timestamp, formatted_date



# Call Option Chain

def stock_ce_option(ticker):
    
    _client = get_session()
    
    expiry = opt_exp(ticker)
    
    a = _client.get_expiry("N", ticker)
    # Returns list of all active expiries

    expiry_list = pd.DataFrame(a['Expiry'])

    spot_price = a['lastrate'][0]['LTP']

    # Apply the function to create new columns
    expiry_list['Timestamp'], expiry_list['Format'] = zip(*expiry_list['ExpiryDate'].apply(process_expiry_date))

    timestamp = expiry_list[expiry_list.Format == expiry].Timestamp.values[0]

    # client.get_option_chain("N","NIFTY",<Pass expiry timestamp from get_expiry response>)
    option_chain = _client.get_option_chain("N", ticker, timestamp)

    option_chain = pd.DataFrame(option_chain['Options'])

    option_chain = option_chain[option_chain.CPType != 'PE']

    option_chain = option_chain[option_chain.LastRate != 0]

    option_chain['SPOT'] = spot_price

    startTime = dt.datetime.today()
    date_obj = dt.datetime.strptime(expiry, "%d %b %Y")  

    daysToExpiry = (date_obj - startTime).days

    CEDelta = []
    r = 10

    if daysToExpiry == 0:
        daysToExpiry = 1
    if daysToExpiry == -1:
        daysToExpiry = 1

    opt_pe_data = pd.DataFrame()

    opt_pe_data['SPOT'] = option_chain['SPOT']
    opt_pe_data['STRIKE'] = option_chain['StrikeRate']
    opt_pe_data['CE_LTP'] = option_chain['LastRate']
    opt_pe_data['SYMBOL'] = option_chain['Name']

    opt_pe_data = opt_pe_data.reset_index(drop=True)    

    for i in range(0, len(opt_pe_data)):
        
        c = mb.BS([opt_pe_data['SPOT'][i],opt_pe_data['STRIKE'][i],r,daysToExpiry], callPrice = opt_pe_data['CE_LTP'][i])
        
        civ = c.impliedVolatility        
        
        cg = mb.BS([opt_pe_data['SPOT'][i],opt_pe_data['STRIKE'][i],r,daysToExpiry], volatility = civ)
              
        cdelta = cg.callDelta
        CEDelta.append(cdelta)

    opt_pe_data['callDel'] = CEDelta
    opt_pe_data['CE_Delta'] = opt_pe_data['callDel']*(100)
    
    
    SPREAD_DELTA_30 = (opt_pe_data['CE_Delta']-SPREAD_DELTA).abs().idxmin()
    SPREAD_DELTA_30_strike = opt_pe_data.loc[SPREAD_DELTA_30,'SYMBOL']    
    
    HEDGE_DELTA_30 = (opt_pe_data['CE_Delta']-HEDGE_DELTA).abs().idxmin()
    HEDGE_DELTA_30_strike = opt_pe_data.loc[HEDGE_DELTA_30,'SYMBOL']
    HEDGE_DELTA_30_strike_PRICE = float(opt_pe_data.loc[HEDGE_DELTA_30,'STRIKE'])
    
    return HEDGE_DELTA_30_strike,HEDGE_DELTA_30_strike_PRICE,SPREAD_DELTA_30_strike
    
#stock_ce_option('NIFTY')
#stock_pe_option('NIFTY')
#stock_ce_option('GAIL')  
#stock_pe_option('NESTLEIND') 


def getting_ohlc():
    global data_list
    data_list.clear()

    for ticker in Tickers:
        retry_count = 0
        while retry_count < 3:
            try:
                print(f"Attempting download for {ticker} (Attempt {retry_count+1}/3)")
                data = get_cash_market_data(ticker, '30m')
                
                # Index formatting
                data.index = data.index.str.split('T').str[0:2]
                data.index = data.index.str.join(' ')
                data.index = pd.to_datetime(data.index, format="%Y-%m-%d %H:%M:%S")
                data.drop(data.tail(1).index,inplace=True)
                
                # Store data
                data_list[ticker] = data
                print(f"✅ Data downloaded for {ticker}")
                break  # Exit loop if success

            except Exception as e:
                print(f"❌ Error for {ticker} (Attempt {retry_count+1}/3): {e}")
                retry_count += 1

                if retry_count == 3:
                    print(f"⛔ Failed to download data for {ticker} after 3 attempts.")


# Finding the Bank Nifty Spot Price
def spot(lt):
    
    _client = get_session()
    
    code = instrument_lookup(symbol=lt)
    
    while True:
        try:
            n = _client.fetch_market_depth([{"Exchange":"N","ExchangeType":"C","ScripCode":str(code)}])
            return n['Data'][0]['LastTradedPrice']
        except TypeError:
            print("TypeError: 'NoneType' object is not subscriptable, retrying...")
            continue
        
# finding ltp for NSE Derivatives
def ltp(lt):
    
    _client = get_session()
    
    code = instrument_lookup(symbol=lt)
    
    while True:
        try:
            n = _client.fetch_market_depth([{"Exchange":"N","ExchangeType":"D","ScripCode":str(code)}])
            return n['Data'][0]['LastTradedPrice']
        except TypeError:
            print("TypeError: 'NoneType' object is not subscriptable, retrying...")
            continue  
    
    
def first_bid(lt):
    
    _client = get_session()
    
    code = instrument_lookup(symbol=lt)
    
    while True:
        try:
            n = _client.fetch_market_depth_by_scrip(Exchange="N",ExchangeType="D",ScripCode=str(code))

            return n['MarketDepthData'][0]['Price']
        except TypeError:
            print("TypeError: 'NoneType' object is not subscriptable, retrying...")
            continue   


def first_ask(lt):
    
    _client = get_session()
    
    code = instrument_lookup(symbol=lt)
    
    while True:
        try:
            n = _client.fetch_market_depth_by_scrip(Exchange="N",ExchangeType="D",ScripCode=str(code))

            return n['MarketDepthData'][5]['Price']
        except TypeError:
            print("TypeError: 'NoneType' object is not subscriptable, retrying...")
            continue 
        


#first_bid('GAIL 28 AUG 2025 CE 182.50')
#first_ask('GAIL 28 AUG 2025 CE 182.50')

        
    
    
required_times = [(9,20),(9, 45), (10, 15), (10, 45), (11, 15), (11, 45), (12, 15), (12, 45), (13, 15),(13, 45), (14, 15), (14, 45), (15, 15)]


# Define a function to check if the current time matches any of the required times
def is_required_time():
    current_time = dt.datetime.now(pytz.timezone('Asia/Kolkata')).time()
    return any(current_time.hour == hour and current_time.minute == minute for hour, minute in required_times)   


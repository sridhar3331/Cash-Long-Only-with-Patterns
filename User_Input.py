import os
working_dir = os.chdir(r"D:\ALGO TRADING\LIVE\ZERODHA CASH")
import pandas as pd
import requests


# User Inputs
START_TIME = [9,15,0]  # Algo Start Time
EXIT_TIME = [15,30,0]  # Algo End Time

Total_Cash_per_position = 60000

Long_max_open_trade = 2

max_hedge = 2

Hedge_Treshold = 0.01 # Hedge will Added if Price Droped 1% from Buy Price

SPREAD_DELTA = 10

HEDGE_DELTA = 30 

lot = 1


# SELECTING STOCKS FOR EACH TICKERS
RISING_WEDGE_A_LONG_Tickers = ['ALKEM','ASIANPAINT', 'ASTRAL', 'BAJAJ-AUTO', 'DABUR', 'DMART', 'GODREJCP','HDFCBANK', 'HCLTECH', 'HEROMOTOCO', 'ICICIGI', 'ICICIPRULI', 'INFY', 'ITC','KOTAKBANK','LT', 'M&M', 'MARUTI', 'NESTLEIND', 'PETRONET', 'PIIND', 'SBIN', 'SHRIRAMFIN', 'SIEMENS', 'SUNPHARMA','TATACONSUM', 'TMPV', 'TATAPOWER', 'TATATECH', 'TCS', 'TITAN', 'ULTRACEMCO', 'VOLTAS']

RISING_WEDGE_C_LONG_Tickers = ['ALKEM','ASIANPAINT', 'ASTRAL', 'BAJAJ-AUTO', 'DABUR', 'DMART', 'GODREJCP','HDFCBANK', 'HEROMOTOCO', 'INFY', 'ITC','KOTAKBANK','LT', 'M&M', 'MARUTI', 'NESTLEIND', 'PIIND', 'SBIN', 'SIEMENS', 'SUNPHARMA', 'TATACONSUM', 'TMPV', 'TATAPOWER', 'TCS', 'TITAN', 'ULTRACEMCO', 'VOLTAS']

RISING_WEDGE_3P_LONG_Tickers = ['ALKEM','ASIANPAINT', 'ASTRAL', 'BAJAJ-AUTO', 'DABUR', 'DMART', 'GODREJCP','HDFCBANK','HCLTECH', 'HEROMOTOCO', 'ICICIGI', 'ICICIPRULI', 'INFY', 'ITC','KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NESTLEIND', 'PETRONET', 'PIIND', 'SBIN', 'SHRIRAMFIN', 'SIEMENS', 'SUNPHARMA', 'TATACONSUM', 'TMPV', 'TATAPOWER', 'TCS', 'TITAN', 'ULTRACEMCO', 'VOLTAS']

set_RISING_WEDGE_A_LONG_Tickers = set(RISING_WEDGE_A_LONG_Tickers)

set_RISING_WEDGE_C_LONG_Tickers = set(RISING_WEDGE_C_LONG_Tickers)

set_RISING_WEDGE_3P_LONG_Tickers = set(RISING_WEDGE_3P_LONG_Tickers)



# for my Testing Bots alerts
def tele_msg(msg):
        
    # Replace YOUR_BOT_TOKEN with your bot token obtained from BotFather
    bot_token = '6xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    
    # Replace CHAT_ID with the ID of the chat you want to send the message to
    chat_id = '-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    
    # Replace MESSAGE_TEXT with the text of the message you want to send
    message_text ="🟩 ZERODHA SRIDHAR LIVE CASH TRADES "+ msg
    
    # Send the message using the sendMessage method of the Telegram Bot API
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message_text}'
    response = requests.get(url) 


# Getting Instrument
instrument_df = pd.read_csv('scripmaster.csv')
instrument_df = instrument_df[(instrument_df.Exch == 'N')]

masterdf = instrument_df[(instrument_df.ScripType == 'XX')&(instrument_df.Series == 'XX')&(instrument_df.Exch == 'N')]

masterdf = masterdf[(masterdf.ExchType == 'D')]


# Filter out rows where 'Name' column has alphanumeric values
sorted_df = masterdf[~masterdf['SymbolRoot'].str.contains(r'\d')]

# Ensure 'Expiry' is in datetime format
sorted_df['Expiry'] = pd.to_datetime(sorted_df['Expiry'])

# Sort ticker by ticker based on 'ContractExpiration'
sorted_df = sorted_df.sort_values(by=['SymbolRoot', 'Expiry'])

# Drop duplicates while keeping the first occurrence based on 'Name'
unique_df = sorted_df.groupby('SymbolRoot').first().reset_index()   

# All Tickers
all_ticker = unique_df['SymbolRoot'].to_list()


# Prepare the qty_dict based on the LotSize, only including tickers in the provided list
qty_dict = {row['SymbolRoot']: {'qty': row['LotSize'] * lot} for index, row in unique_df.iterrows() if row['SymbolRoot'] in all_ticker}

# Function to remove non-existent tickers
def remove_non_existent_tickers(all_ticks, tickers, list_name):
    for ticker in tickers[:]:
        if ticker not in all_ticks:
            tele_msg(f'{ticker} from {list_name} does not exist in Future and Option Segment.')
            tickers.remove(ticker)


Tic = list(set_RISING_WEDGE_A_LONG_Tickers | set_RISING_WEDGE_C_LONG_Tickers | set_RISING_WEDGE_3P_LONG_Tickers)

Tic.sort()

# Apply the function to each list
remove_non_existent_tickers(all_ticker, Tic, 'Tickers')

Tickers = Tic







'''
RISING_WEDGE_A_LONG_Tickers = ['ALKEM', 'AMBUJACEM', 'APLAPOLLO', 'ASIANPAINT', 'ASTRAL', 'AUROPHARMA', 'BAJAJ-AUTO', 'CIPLA', 'COLPAL', 'CROMPTON', 'DABUR', 'DIVISLAB', 'DMART', 'GODREJCP', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'ICICIGI', 'ICICIPRULI', 'INFY', 'IRCTC', 'ITC', 'KOTAKBANK', 'LT', 'MANKIND', 'MAXHEALTH', 'NAUKRI', 'NESTLEIND', 'PERSISTENT', 'PETRONET', 'PIIND', 'POWERGRID', 'PPLPHARMA', 'RELIANCE', 'SBILIFE', 'SBIN', 'SHRIRAMFIN', 'SIEMENS', 'SRF', 'SUNPHARMA', 'TATACONSUM', 'TATAELXSI', 'TATAMOTORS', 'TATAPOWER', 'TATATECH', 'TCS', 'TITAN', 'TORNTPOWER', 'TRENT', 'ULTRACEMCO', 'VOLTAS']

RISING_WEDGE_C_LONG_Tickers = ['ALKEM', 'AMBUJACEM', 'APLAPOLLO', 'ASIANPAINT', 'AUROPHARMA', 'BAJAJ-AUTO', 'CIPLA', 'DABUR', 'DIVISLAB', 'DMART', 'GODREJCP', 'HCLTECH', 'HDFCBANK', 'ICICIPRULI', 'INFY', 'IRCTC', 'ITC', 'KOTAKBANK', 'LT', 'PERSISTENT', 'PETRONET', 'PIIND', 'POWERGRID', 'PPLPHARMA', 'RELIANCE', 'SBILIFE', 'SBIN', 'SIEMENS', 'SRF', 'SUNPHARMA', 'TATACONSUM', 'TATAELXSI', 'TATAMOTORS', 'TATAPOWER', 'TCS', 'TITAN', 'TORNTPOWER', 'TRENT', 'ULTRACEMCO', 'VOLTAS']

RISING_WEDGE_3P_LONG_Tickers = ['ALKEM', 'AMBUJACEM', 'APLAPOLLO', 'ASIANPAINT', 'ASTRAL', 'AUROPHARMA', 'BAJAJ-AUTO', 'CIPLA', 'COLPAL', 'DABUR', 'DIVISLAB', 'DMART', 'GODREJCP', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'ICICIGI', 'ICICIPRULI', 'INFY', 'IRCTC', 'ITC', 'KOTAKBANK', 'LT', 'MANKIND', 'MAXHEALTH', 'NESTLEIND', 'PERSISTENT', 'PETRONET', 'PIIND', 'POWERGRID', 'PPLPHARMA', 'RELIANCE', 'SBILIFE', 'SBIN', 'SHRIRAMFIN', 'SIEMENS', 'SRF', 'SUNPHARMA', 'TATACONSUM', 'TATAELXSI', 'TATAMOTORS', 'TATAPOWER', 'TCS', 'TITAN', 'TORNTPOWER', 'TRENT', 'ULTRACEMCO', 'VOLTAS']

RISING_WEDGE_3P_SHORT_Tickers = ['ALKEM', 'AMBUJACEM', 'APLAPOLLO', 'ASIANPAINT', 'ASTRAL', 'AUROPHARMA', 'CROMPTON', 'DABUR', 'GRASIM', 'HCLTECH', 'ICICIPRULI', 'INFY', 'IRCTC', 'KOTAKBANK', 'NESTLEIND', 'PETRONET', 'POWERGRID', 'PPLPHARMA', 'RELIANCE', 'SBIN', 'SIEMENS', 'SRF', 'SUNPHARMA', 'TATACONSUM', 'TATAELXSI', 'TATAMOTORS', 'TATAPOWER', 'TATATECH', 'TCS', 'TITAN', 'TORNTPOWER', 'ULTRACEMCO', 'VOLTAS']

Short_Reversal_A_Entry_SHORT_Tickers = ['ALKEM', 'AMBUJACEM', 'APLAPOLLO', 'ASIANPAINT', 'ASTRAL', 'AUROPHARMA', 'BAJAJ-AUTO', 'CIPLA', 'COLPAL', 'DABUR', 'DMART', 'GODREJCP', 'HCLTECH', 'ICICIGI', 'ICICIPRULI', 'INFY', 'ITC', 'KOTAKBANK', 'PERSISTENT', 'PETRONET', 'POWERGRID', 'PPLPHARMA', 'RELIANCE', 'SBIN', 'SHRIRAMFIN', 'SIEMENS', 'SRF', 'SUNPHARMA', 'TATAMOTORS', 'TATAPOWER', 'TATATECH', 'TCS', 'TITAN', 'TORNTPOWER', 'TRENT', 'ULTRACEMCO']


'''

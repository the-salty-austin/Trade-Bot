import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
# from tqdm import tqdm_notebook #(Optional, used for progress-bars)

import CRYPTO_config

# https://medium.com/swlh/retrieving-full-historical-data-for-every-cryptocurrency-on-binance-bitmex-using-the-python-apis-27b47fd8137f

binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
batch_size = 750
binance_client = Client(CRYPTO_config.apiKey, CRYPTO_config.apiSecurity)


def minutes_of_new_data(symbol, kline_size, data, source):
    if len(data) > 0:  old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance": old = datetime.strptime('1 Jan 2017', '%d %b %Y')
    
    if source == "binance": new = pd.to_datetime( binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms' )
    '''
    binance_client.get_klines(*) returns "current data"
    [
        [
            1499040000000,      # Open time
            "0.01634790",       # Open
            "0.80000000",       # High
            "0.01575800",       # Low
            "0.01577100",       # Close
            "148976.11427815",  # Volume
            1499644799999,      # Close time
            "2434.19055334",    # Quote asset volume
            308,                # Number of trades
            "1756.87402397",    # Taker buy base asset volume
            "28.46694368",      # Taker buy quote asset volume
            "17928899.62484339" # Can be ignored
        ]
    ]
    '''
    return old, new

def get_all_binance(symbol, kline_size, save = False):
    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename): data_df = pd.read_csv(filename)
    else: data_df = pd.DataFrame()
    
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source="binance")
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil( delta_min/binsizes[kline_size] )
    
    print(oldest_point, newest_point, available_data, type(oldest_point))
    
    if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'):
        all_confirm = input('Are you sure to download all data from 1 Jan 2017? (Y/N) ')
        if all_confirm == 'Y':
            print('Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol))
        else:
            oldest_point = input('YYYY-MM-DD HH:MM:SS ')
            oldest_point = datetime. strptime(oldest_point, '%Y-%m-%d %H:%M:%S')
            print('Downloading data since %s for %s. Be patient..!' % (oldest_point, symbol))
    
    else: print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (delta_min, symbol, available_data, kline_size))
    
    klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))
    data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else: data_df = data
    data_df.set_index('timestamp', inplace=True)
    if save: data_df.to_csv('./csv/'+filename)
    print('All caught up..!')
    return data_df

if __name__ == '__main__':
    # data = get_all_binance('BTCUSDT', '1m', save=False)
    data = get_all_binance('BTCUSDT', '1d', save=True )
    print(data)
    print(data.columns)

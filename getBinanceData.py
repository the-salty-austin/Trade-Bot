import pandas as pd
import math
# import os.path
# import time
from binance.client import Client
from datetime import timedelta, datetime
# from dateutil import parser
# from tqdm import tqdm_notebook #(Optional, used for progress-bars)

import CRYPTO_config
from CRYPTO_technical_analysis import TA

# https://medium.com/swlh/retrieving-full-historical-data-for-every-cryptocurrency-on-binance-bitmex-using-the-python-apis-27b47fd8137f
'''
download current price data from Binance API
then calculate TA
'''

binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
batch_size = 750
binance_client = Client(CRYPTO_config.apiKey, CRYPTO_config.apiSecurity)


def minutes_of_new_data(symbol, kline_size, source):
    if source == "binance":
        old = datetime.strptime('1 Jan 2017', '%d %b %Y')
        new = pd.to_datetime( binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms' )
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

def get_all_binance(symbol, kline_size):
    data_df = pd.DataFrame()
    
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, source="binance")
    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil( delta_min/binsizes[kline_size] )
    
    print(oldest_point, newest_point, available_data, type(oldest_point))
     
    klines = binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S"))
    # print(klines)
    data = pd.DataFrame(klines, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    
    return data

def calculate_ta(symbol, interval='1d'):
    df = get_all_binance(symbol, interval)
    print(df)
    print(df.columns)
    df.drop(['open', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'], axis=1, inplace=True)
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

    df['price_diff'] = df['close'].diff()

    df['MA_05'] = TA.moving_average( df['close'] , window_size=5 )
    df['MA_10'] = TA.moving_average( df['close'] , window_size=10 )
    df['MA_20'] = TA.moving_average( df['close'] , window_size=20 )

    df['RSI_06'] = TA.relative_strength_index(df['price_diff'], window_size=6)  # OKAY
    df['RSI_12'] = TA.relative_strength_index(df['price_diff'], window_size=12)  # OKAY
    df['RSI_24'] = TA.relative_strength_index(df['price_diff'], window_size=24)  # OKAY

    df['EMA_12'] = TA.exponential_moving_average(df['close'] , window_size=12)  # OKAY
    df['EMA_26'] = TA.exponential_moving_average(df['close'] , window_size=26)  # OKAY

    df['MACD'], df['Signal'], df['Histogram'] = TA.macd(df['EMA_12'], df['EMA_26'])  # OKAY

    df['K%'], df['D%'] = TA.stochastic_oscillator(df['close'], window_size=9)  # OKAY

    return df

if __name__ == '__main__':
    # df = get_all_binance('BTCUSDT', '1m', save=False)
    df = calculate_ta('BTCUSDT')
    # print(df.head(6))
    # print(df.tail(6))
    # print(df.columns)
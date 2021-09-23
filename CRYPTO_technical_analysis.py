import csv
import math
import time
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import talib

class Utility:
    @staticmethod
    def read_csv(fname: str) -> pd.DataFrame:
        data = pd.read_csv(fname)
        return data

    @staticmethod
    def save_to_csv(data: pd.DataFrame, fname='test.csv') -> None:
        data.to_csv('./csv_ta/'+fname, sep=',')

class TA:
    # TA == Technical_Analysis
    @staticmethod
    def moving_average(data: pd.DataFrame, window_size=5, update=False) -> list:
        i = 0
        moving_averages = [None]*(window_size-1)
        while i < len(data) - window_size + 1:
            this_window = data[i : i + window_size]
            window_average = sum(this_window) / window_size
            moving_averages.append(window_average)
            i += 1

        # print(moving_averages)
        # print('\n',len(moving_averages),'\n')
        return moving_averages

    @staticmethod
    def relative_strength_index(df_chg: pd.DataFrame, window_size=14, update=False) -> pd.DataFrame:
        df = pd.DataFrame()
        df['chg'] = df_chg
        df['gain'] = df_chg.mask(df_chg < 0, 0.0)
        df['loss'] = -df_chg.mask(df_chg > 0, -0.0)

        # <NOTE> Some RSI calculation method uses SMA. Here, EMA is used.
        # somehow, for RSI, Binance(?) calculates ALPHA in EMA differently ==> [ USE_OLD_ALPHA=False ]
        # See [ exponential_moving_average( *args ) ] for details
        df['avg_gain'] = TA.exponential_moving_average(df['gain'], window_size=window_size, USE_OLD_ALPHA=False)
        df['avg_loss'] = TA.exponential_moving_average(df['loss'], window_size=window_size, USE_OLD_ALPHA=False)
        df['rs'] = df.avg_gain / df.avg_loss
        df[f'rsi_{window_size}'] = 100 - (100 / (1 + df.rs))

        return df[f'rsi_{window_size}']

    @staticmethod
    def exponential_moving_average(df_close: pd.DataFrame, window_size=5, USE_OLD_ALPHA=True, update=False) -> list:
        df_ma = TA.moving_average(df_close, window_size=window_size)
        ema = [None]*(window_size-1) + [ df_close[:window_size].mean() ]

        # The "weight (ALPHA)" can be slightly different 
        if USE_OLD_ALPHA: ALPHA = float(2)/(window_size+1)
        else: ALPHA = 1.0/window_size

        i = 0
        while i < len(df_ma) - window_size:
            window_val = ALPHA*df_close.iloc[window_size+i] + (1-ALPHA)*ema[window_size+i-1]
            ema.append(window_val)
            i += 1

        return ema

    @staticmethod
    def macd(ema12s: pd.DataFrame, ema26s: pd.DataFrame, update=False) -> tuple:
        '''<return lists> dif, dem, hist'''
        length = len(ema12s)
        dif = [None]*(25)  # 26-1 QUICK
        dem = [None]*(25)  # 26-1 SLOW
        hist = [None]*(34)  # 26-1+9 ==> QUICK-SLOW
        for ema12, ema26 in zip(ema12s[25:], ema26s[25:]):
            dif.append( ema12-ema26 )

        tmp_df = pd.DataFrame(dif[25:])
        dem_res = TA.exponential_moving_average(tmp_df, window_size=9)
        for i, x in enumerate(dem_res):
            if x is None: continue
            dem_res[i] = x.item()
        dem += dem_res
        
        for i in range(34, length):
            window_expavg = dem[i]
            hist.append( dif[i]-window_expavg )
        
        print(type(dem[-2]), type(hist[-2]))
        print(dem[:4],dem[-5:])
        print(hist[-5:])

        return dif, dem, hist

    @staticmethod
    def stochastic_oscillator(df_close: pd.DataFrame, window_size=5, update=False) -> tuple:
        '''<return tuple of LISTS>\n
        [1] K [2] D'''
        length = len(df_close)
        Ks = [None]*(window_size)
        Ds = [None]*(window_size)  # 3-1

        window = df_close[0:window_size]
        # print(window)
        high = max(window)
        low = min(window)
        # print(high,low, df_close.iloc[window_size-1])
        k0 = 100 * (df_close.iloc[window_size-1]-low) / (high-low)
        d0 = k0
        Ks.append(k0)
        Ds.append(d0)
        # print(Ks)
        # print(Ds)
        
        for i in range(window_size+1, length):
            prev_k = Ks[i-1]
            prev_d = Ds[i-1]
            window = df_close[i+1-window_size:i+1]
            high = max(window)
            low = min(window)

            rsv = 100 * (df_close.iloc[i]-low) / (high-low)  # Raw Stochastic Value
            # print(i, prev_k, rsv)
            k = prev_k*(2/3) + rsv*(1/3)
            d = prev_d*(2/3) +  k *(1/3)
            Ks.append(k)
            Ds.append(d)

        # print(Ks[-5:])
        # print('')
        # print(Ds[-5:])

        return Ks, Ds


# ============================ [ MAIN FUNCTION ] ===================================

def main():
    df = Utility.read_csv("./csv/BTCUSDT-1d-data.csv")
    df.drop(['open', 'close_time', 'ignore'], axis=1, inplace=True)

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

    # print(df.head(6))
    # print(df.tail(6))
    # print(df.columns)

    print(df['K%'])
    Utility.save_to_csv(df, fname='TEST2.csv')

if __name__ == '__main__':
    main()
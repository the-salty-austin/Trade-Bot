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
    def moving_average(df_close: pd.DataFrame, window_size=5, update=False, old_close=None) -> list:
        if not update:
            i = 0
            moving_averages = [None]*(window_size-1)

            while i < len(df_close) - window_size + 1:
                this_window = df_close[i : i + window_size]
                window_average = sum(this_window) / window_size
                moving_averages.append(window_average)
                i += 1
        
        elif update:
            i = 0
            old_close = list(old_close[-window_size:])
            # print(old_close)
            moving_averages = []
            while i < len(df_close):
                if i < window_size-1:
                    this_window = old_close[-window_size+i+1:] + list(df_close[:i+1])
                    
                elif i >= window_size-1:
                    this_window = df_close[i+1-window_size:i+1]
                
                window_average = sum(this_window) / window_size
                moving_averages.append( window_average )
                i += 1

        # print('HERE', len(moving_averages), moving_averages)
        return moving_averages

    @staticmethod
    def relative_strength_index(df_chg: pd.DataFrame, window_size=14, update=False, old_gain=None, old_loss=None) -> pd.DataFrame:
        df = pd.DataFrame()
        df['chg'] = df_chg
        df['gain'] = df_chg.mask(df_chg < 0, 0.0)
        df['loss'] = -df_chg.mask(df_chg > 0, -0.0)

        if not update:
            # <NOTE> Some RSI calculation method uses SMA. Here, EMA is used.
            # somehow, for RSI, Binance(?) calculates ALPHA in EMA differently ==> [ USE_OLD_ALPHA=False ]
            # See [ exponential_moving_average( *args ) ] for details
            df['avg_gain'] = TA.exponential_moving_average(df['gain'], window_size=window_size, USE_OLD_ALPHA=False)
            df['avg_loss'] = TA.exponential_moving_average(df['loss'], window_size=window_size, USE_OLD_ALPHA=False)

        elif update:
            df['avg_gain'] = TA.exponential_moving_average(df['gain'], window_size=window_size, USE_OLD_ALPHA=False, update=True, old_ema=old_gain)
            df['avg_loss'] = TA.exponential_moving_average(df['loss'], window_size=window_size, USE_OLD_ALPHA=False, update=True, old_ema=old_loss)

        df['rs'] = df.avg_gain / df.avg_loss
        df[f'rsi_{window_size}'] = 100 - (100 / (1 + df.rs))

        return df[f'rsi_{window_size}'], df['avg_gain'], df['avg_loss']

    @staticmethod
    def exponential_moving_average(df_close: pd.DataFrame, window_size=5, USE_OLD_ALPHA=True, update=False, old_ema=None) -> list:
        # The "weight (ALPHA)" can be slightly different 
        if USE_OLD_ALPHA: ALPHA = float(2)/(window_size+1)
        else: ALPHA = 1.0/window_size
        
        if not update:
            df_ma = TA.moving_average(df_close, window_size=window_size)
            ema = [None]*(window_size-1) + [ df_close[:window_size].mean() ]

            i = 0
            while i < len(df_ma) - window_size:
                window_val = ALPHA*df_close.iloc[window_size+i] + (1-ALPHA)*ema[window_size+i-1]
                ema.append(window_val)
                i += 1

        elif update:
            old_last = old_ema.iloc[-1]
            # print(old_last)
            # print( df_close )
            ema = [ old_last ]
            i = 0
            while i < len(df_close):
                window_val = ALPHA*df_close.iloc[i] + (1-ALPHA)*ema[i]
                ema.append(window_val)
                i += 1
            ema = ema[1:]
            # print(ema, len(ema))

        return ema

    @staticmethod
    def macd(ema12s: pd.DataFrame, ema26s: pd.DataFrame, update=False, old_dem=None) -> tuple:
        '''<return lists> dif, dem, hist'''
        if not update:
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
            
            # print(type(dem[-2]), type(hist[-2]))
            # print(dem[:4],dem[-5:])
            # print(hist[-5:])

        elif update:
            length = len(ema12s)
            dif = []  # QUICK
            dem = []  # SLOW
            hist = []  # QUICK-SLOW
            for ema12, ema26 in zip(ema12s, ema26s):
                dif.append( ema12-ema26 )

            tmp_df = pd.DataFrame(dif)
            dem_res = TA.exponential_moving_average(tmp_df, window_size=9, update=True, old_ema=old_dem)
            # print(dem_res)
            # x=input()
            for i, x in enumerate(dem_res):
                dem_res[i] = x.item()
            dem += dem_res
            
            for i in range(length):
                window_expavg = dem[i]
                hist.append( dif[i]-window_expavg )

        return dif, dem, hist

    @staticmethod
    def stochastic_oscillator(df_close: pd.DataFrame, window_size=5, update=False, old_close=None, old_k=None, old_d=None) -> tuple:
        '''<return tuple of LISTS>\n
        [1] K [2] D'''
        if not update:
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

        elif update: 
            Ks = []
            Ds = []

            for i in range( len(df_close) ):
                if i < window_size-1:
                    window = list( old_close.iloc[-window_size+i+1:] ) + list( df_close.iloc[:i+1] )
                else:
                    window = list( df_close.iloc[i+1-window_size:i+1] )
                
                high = max(window)
                low = min(window)

                rsv = 100 * (df_close.iloc[i]-low) / (high-low)  # Raw Stochastic Value
                
                if i == 0:
                    prev_d = old_d.iloc[-1]
                    prev_k = old_k.iloc[-1]
                else: 
                    prev_d = Ds[i-1]
                    prev_k = Ks[i-1]
                
                k = prev_k*(2/3) + rsv*(1/3)
                d = prev_d*(2/3) +  k *(1/3)
                Ks.append(k)
                Ds.append(d)

        return Ks, Ds


# ============================ [ MAIN FUNCTION ] ===================================

def main():
    df = Utility.read_csv("./csv/BTCUSDT-1d-data.csv")
    df.drop(['open', 'close_time', 'ignore'], axis=1, inplace=True)

    df['price_diff'] = df['close'].diff()

    df['MA_05'] = TA.moving_average( df['close'] , window_size=5 )
    df['MA_10'] = TA.moving_average( df['close'] , window_size=10 )
    df['MA_20'] = TA.moving_average( df['close'] , window_size=20 )

    df['RSI_06'], df['EMA06_Gain'], df['EMA06_Loss'] = TA.relative_strength_index(df['price_diff'], window_size=6)  # OKAY
    df['RSI_12'], df['EMA12_Gain'], df['EMA12_Loss'] = TA.relative_strength_index(df['price_diff'], window_size=12)  # OKAY
    df['RSI_24'], df['EMA24_Gain'], df['EMA24_Loss'] = TA.relative_strength_index(df['price_diff'], window_size=24)  # OKAY

    df['EMA_12'] = TA.exponential_moving_average(df['close'] , window_size=12)  # OKAY
    df['EMA_26'] = TA.exponential_moving_average(df['close'] , window_size=26)  # OKAY

    df['MACD'], df['Signal'], df['Histogram'] = TA.macd(df['EMA_12'], df['EMA_26'])  # OKAY

    df['K%'], df['D%'] = TA.stochastic_oscillator(df['close'], window_size=9)  # OKAY

    # print(df.head(6))
    # print(df.tail(6))
    # print(df.columns)

    # print(df['K%'])
    Utility.save_to_csv(df, fname='TEST3.csv')

if __name__ == '__main__':
    main()
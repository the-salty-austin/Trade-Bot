import pandas as pd
from CRYPTO_technical_analysis_extend import TA, Utility

fname = 'D:\\Python\\2021 Stock\\csv_ta\\TEST3.csv'
with open(fname) as csv_file:
    header = []
    data = []
    for i, row in enumerate(csv_file):
        if i == 0:
            header = row.strip().split(',')[1:]
            continue
        data.append( row.strip().split(',')[1:] )

    data = data[-31:]
    # print(header)
    df_old = pd.DataFrame(data, columns=header)
    for column_name in header[1:]:
        # skip 'time stamp'
        df_old[column_name] = pd.to_numeric(df_old[column_name], errors='coerce')
    
    df_old = df_old.iloc[:-1]

    df_new = Utility.read_csv("./csv/BTCUSDT-1d-data_extend.csv")
    df_new.drop(['open', 'close_time', 'ignore'], axis=1, inplace=True)

    df_new['MA_05'] = TA.moving_average(df_new['close'], window_size= 5, update=True, old_close=df_old['close'])  # OKAY
    df_new['MA_10'] = TA.moving_average(df_new['close'], window_size=10, update=True, old_close=df_old['close'])  # OKAY
    df_new['MA_20'] = TA.moving_average(df_new['close'], window_size=20, update=True, old_close=df_old['close'])  # OKAY
   
    close = df_old['close'][-1:].append( df_new['close'] )
    df_new['price_diff'] = close.diff()[1:]

    df_new['RSI_06'], df_new['EMA06_Gain'], df_new['EMA06_Loss'] = TA.relative_strength_index(df_new['price_diff'], window_size= 6, update=True, old_gain=df_old['EMA06_Gain'], old_loss=df_old['EMA06_Loss'])
    df_new['RSI_12'], df_new['EMA12_Gain'], df_new['EMA12_Loss'] = TA.relative_strength_index(df_new['price_diff'], window_size=12, update=True, old_gain=df_old['EMA12_Gain'], old_loss=df_old['EMA12_Loss'])
    df_new['RSI_24'], df_new['EMA24_Gain'], df_new['EMA24_Loss'] = TA.relative_strength_index(df_new['price_diff'], window_size=24, update=True, old_gain=df_old['EMA24_Gain'], old_loss=df_old['EMA24_Loss'])
    
    df_new['EMA_12'] = TA.exponential_moving_average(df_new['close'], window_size=12, update=True, old_ema=df_old['EMA_12'])  # slight error
    df_new['EMA_26'] = TA.exponential_moving_average(df_new['close'], window_size=26, update=True, old_ema=df_old['EMA_26'])  # slight error
    
    print(df_new[ ['timestamp', 'close', 'MA_05', 'MA_10', 'MA_20', 'RSI_06', 'RSI_12', 'RSI_24', 'EMA_12', 'EMA_26'] ] )

    df_new['MACD'], df_new['Signal'], df_new['Histogram'] = TA.macd(df_new['EMA_12'], df_new['EMA_26'], update=True, old_dem=df_old['Signal'])  # slight error
    
    print(df_old[ ['timestamp', 'close', 'MACD', 'Signal', 'Histogram'] ] )
    print(df_new[ ['timestamp', 'close', 'MACD', 'Signal', 'Histogram'] ] )

    # Update gone  WRONG!!
    df_new['K%'], df_new['D%'] = TA.stochastic_oscillator(df_new['close'], window_size=9, update=True, old_close=df_old['close'], old_k=df_old['K%'], old_d=df_old['D%'])  # OKAY
   
    print(df_old[ ['timestamp', 'close', 'K%', 'D%'] ] )
    print(df_new[ ['timestamp', 'close', 'K%', 'D%'] ] )
    
    # df_combined = df_old.iloc[:-1].append( df_new , ignore_index=True )
    # print(df_combined)

# API key / security
import CRYPTO_config

# import from jere
from binance.client import Client
import websocket, json

# extra import
import time
from datetime import datetime
import CRYPTO_database as db

# client = Client(config.apiKey,config.apiSecurity)
# print('#####  logged in  #####')

# info = client.get_symbol_info('BNBBTC')
# print(info)

# for i in info:
#     print(i)

cc = 'btcusd'  # crypto currency
interval = '1h'

socket= f'wss://stream.binance.com:9443/ws/{cc}t@kline_{interval}'

print(socket)

closes, highs, lows = [], [], []

def on_message(ws, message):
    # print(message)
    json_message = json.loads(message)
    # print(json_message)
    '''
    {'e': 'kline',  # Event Type
     'E': 1624969604073,  # Event Time
     's': 'BTCUSDT',  # Symbol
     'k':{
         't': 1624969560000,  # kline Start Time
         'T': 1624969619999,  # kline Close Time
         's': 'BTCUSDT',  # Symbol
         'i': '1m',  # Interval
         'f': 938326677,  # First trade ID
         'L': 938327825,  # Last trade ID
         'o': '35723.96000000',  # Open Price
         'c': '35760.00000000',  # Close Price
         'h': '35765.83000000',  # High Price
         'l': '35690.33000000',  # Low Price
         'v': '70.36781000',  # Base Assert Volume
         'n': 1149,  # Number of Trades
         'x': False,  # binary: whether closed or not
         'q': '2513379.72294587',  # Quote Asset Volume
         'V': '41.35311100',  # Taker Buy Base Asset Volume
         'Q': '1477047.88235321',  # Taker Buy Quote Asset Volume
         'B': '0'  # Ignore?
         }
    }
    '''
    # 
    candle = json_message['k']  # sub-dictionary

    is_closed = candle['x']
    time = int(candle['T'])  # close time
    close = float(candle['c'])
    high = float(candle['h'])
    low = float(candle['l'])
    vol = float(candle['v'])

    # if is_closed :
    closes.append( close )
    highs.append( high )
    lows.append( low )

    data = [close, high, low, vol, time]

    db.Save().save(data)

    print(f'Time Now: { datetime.now().strftime("%H:%M:%S") } || Close:{close} High:{high} Low:{low} Vol:{vol}')

    # time.sleep(20)

def on_close(ws):
    print("\n### conn closed ###\n")

ws = websocket.WebSocketApp(socket, on_message = on_message, on_close = on_close)
ws.run_forever()
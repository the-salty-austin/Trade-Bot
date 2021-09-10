from os import close
from bs4 import BeautifulSoup
import requests
import pandas as pd

response = requests.get("https://www.udemy.com/course/codegym-python/")
soup = BeautifulSoup(response.text, "html.parser")

df = pd.DataFrame()
with open('./csv/BTCUSDT-1d-data.csv', mode='r') as f:
    close_lst = []
    for i, line in enumerate(f):
        if i == 0: continue
        # 0 timestamp,1 open,2 high,3 low,4 close,5 volume
        line = line.strip().split(',')
        date = line[0]
        close = float(line[4])
        # volume = line[5]
        close_lst.append( close )
    df['close'] = close_lst
df['diff'] = df['close'].diff()
df['chg'] = df['diff']/df['close']
print(df)

last_chg = df['chg'].iloc[-1]


headers = {
    "Authorization": "Bearer " + "hts3KhZzPE3CK6TGLujohTI8lH6Rky4HOBZ7tiYQax2",
    "Content-Type": "application/x-www-form-urlencoded"
}

if last_chg > 0:
    params = {"message": "\nBitcoin 漲幅" + str(round(last_chg*100, 2)) + "%"}
elif last_chg  < 0:
    params = {"message": "\nBitcoin 跌幅" + str(round(last_chg*100, 2)) + "%"}
 
r = requests.post("https://notify-api.line.me/api/notify",
                    headers=headers, params=params)
print(r.status_code)  #200

import pandas as pd

fname = 'D:\\Python\\2021 Stock\\csv_ta\\TEST1.csv'
with open(fname) as csv_file:
    header = []
    data = []
    print(len(data))
    for i, row in enumerate(csv_file):
        if i == 0:
            header = [row.strip()]
            continue
        data.append( row.strip() )

    
    print(header)
    print(data[0])
    print(data[-1])
    print(len(data))
    data = data[-30:]
    print(len(data))

import urllib3
import json
import datetime
import time
import sys
import glob
import os


#ひとまず1分足 
periods = '60'
targetDate = ''

# CSVからロードしてくる
import pandas as pd
dir = '../executions/'
csv_files = glob.glob(os.path.join(dir,'*.csv'))
df_list = []

for csv_file in csv_files:

    df = pd.read_csv(csv_file, parse_dates=['exec_date'])

    #exec_date列の秒、ミリ秒以下の差異を無視する（1分足にする） 
    df['exec_date'] = df['exec_date'].map(lambda x: x.replace(second=0, microsecond=0))

    #1
    summary = df[['exec_date', 'price']].groupby(['exec_date']).first().rename(columns={'price': 'first'})
    summary = summary.merge(
        df[['exec_date', 'price']].groupby(['exec_date']).max().rename(columns={'price': 'max'}),
        left_index=True, right_index=True)
    summary = summary.merge(
        df[['exec_date', 'price']].groupby(['exec_date']).min().rename(columns={'price': 'min'}),
        left_index=True, right_index=True)
    summary = summary.merge(
        df[['exec_date', 'price']].groupby(['exec_date']).last().rename(columns={'price': 'last'}),
        left_index=True, right_index=True)
    summary = summary.merge(
        df[['exec_date', 'size']].groupby(['exec_date']).sum(),
        left_index=True, right_index=True)

    df_list.append(summary[:])

df_listconcat = pd.concat(df_list, ignore_index=False)

resp = df_listconcat.reset_index().values.tolist()

for r in resp:
    date = str(r[0].to_pydatetime())
    if targetDate in date:
        print(str(r[0].to_pydatetime()) + "," + str(r[1]) + "," + str(r[2]) + "," + str(r[3]) + "," + str(r[4]) + "," + str(r[5]))





import pandas as pd
import KuberIndicators as indicator
import requests
import json
import KuberConfig as mjp
import numpy as np

import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
#Next, log in to the server
server.login("radharani1306@gmail.com", "bobbygadu")


def SMM(ohlc, period=9, column=mjp.CLOSE):
    """
    Simple moving median, an alternative to moving average. SMA, when used to estimate the underlying trend in a time series,
    is susceptible to rare events such as rapid shocks or other anomalies. A more robust estimate of the trend is the simple moving median over n time periods.
    """

    return pd.Series(ohlc[column].rolling(center=False, window=period,
                                          min_periods=period - 1).median(),
                     name='{0} period SMM'.format(period))


pd.set_option('display.expand_frame_repr', False)

df = pd.read_csv("D://10MINTESTING.csv")

df["Date"] = pd.to_datetime(df["Date"])
mask = (df['Date'] > "2018-12-1")

df = df[mask]
df.reset_index(inplace=True)
df["SMM9"] = SMM(df)
print(df.tail())

indicator_column = "SMM9"

df = df[[mjp.DATE,mjp.CLOSE,indicator_column]]

profit = 0
BUY_FLAG = False
SELL_FLAG = False
buy_price = 0
sell_price = 0
PRINT_FLAG = False
#PRINT_FLAG = True
SEND_MAIL_FLAG = False
#SEND_MAIL_FLAG = True


msg = "Subject:Demo\n"
for idx in range(14,len(df.index)):
    #print("super===>", df.loc[idx,"SuperTrend"]," Close===>",df.loc[idx,"Close"])
    indi =int( df.loc[idx,indicator_column])
    close = df.loc[idx,mjp.CLOSE]
    date = df.loc[idx,mjp.DATE]
    if close > indi:        #For Buy purpose
        if sell_price != 0 and SELL_FLAG:
            buy_price = close
            profit += ((sell_price - buy_price) * 100 - 200)
            sell_price = 0
            BUY_FLAG = True
            SELL_FLAG = False
            if PRINT_FLAG:
                dat = input("At {} bought @{} and {} @{} and profit @{}......".format(date,close,indicator_column, super,profit))
            msg += "At {} bought @{} and {} @{} and profit @{}......\n".format(date,close,indicator_column, super,profit)
        elif not BUY_FLAG:
            buy_price = close
            BUY_FLAG = True
            SELL_FLAG = False
            if PRINT_FLAG:
                dat = input("At {} buy @{} and {} @{}......".format(date,close,indicator_column,super))
            msg += "At {} buy @{} and {} @{}......".format(date,close,indicator_column,super)


    else:                    #For Sell purpose
        if buy_price != 0 and BUY_FLAG:
            sell_price = close
            profit += ((sell_price - buy_price) * 100 - 200)
            buy_price = 0
            SELL_FLAG = True
            BUY_FLAG = False
            if PRINT_FLAG:
                dat = input("At {} sold @{} and {} @{} and profit @{}......".format(date,close,indicator_column, super,profit))
            msg += "At {} sold @{} and {} @{} and profit @{}......".format(date,close,indicator_column, super,profit)
        elif not SELL_FLAG:
            sell_price = close
            SELL_FLAG = True
            BUY_FLAG = False
            if PRINT_FLAG:
                dat = input("At {} sell@ {} and {} @ {}......".format(date,close,indicator_column,super))
            msg += "At {} sell@ {} and {} @ {}......".format(date,close,indicator_column,super)

print("profit===>",profit)
msg += "profit===>{}".format(profit)
#print(df.tail())
if SEND_MAIL_FLAG:
    server.sendmail("radharani1306@gmail.com", "pooritrading13@gmail.com", msg)


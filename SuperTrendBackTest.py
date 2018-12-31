import pandas as pd
import KuberIndicators as indicator
import requests
import json
import KuberConfig as mjp
import numpy as np

import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
# server.ehlo()
server.starttls()
#Next, log in to the server
server.login("radharani1306@gmail.com", "bobbygadu")



def average_true_range(df, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        TR = max(df.loc[i + 1, mjp.HIGH], df.loc[i, "MA_8"]) - min(df.loc[i + 1, mjp.LOW], df.loc[i, "MA_8"])
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l)
    ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean(), name='ATR_' + str(n))
    df = df.join(ATR)
    return df


def smoothTriangle(data, degree, dropVals=False):
    """performs moving triangle smoothing with a variable degree."""
    """note that if dropVals is False, output length will be identical
    to input length, but with copies of data at the flanking regions"""
    triangle = np.array(list(range(degree)) + [degree] + list(range(degree))[::-1]) + 1
    smoothed = []
    for i in range(degree, len(data) - degree * 2):
        point = data[i:i + len(triangle)] * triangle
        smoothed.append(sum(point) / sum(triangle))
    if dropVals: return smoothed
    smoothed = [smoothed[0]] * int(degree + degree / 2) + smoothed
    while len(smoothed) < len(data): smoothed.append(smoothed[-1])
    return smoothed

def ST(df, n, f):  # df is the dataframe, n is the period, f is the factor; f=3, n=7 are commonly used.
    # Calculation of SuperTrend

    atr = 'ATR_' + str(n)
    df['Upper Basic'] = (df[mjp.HIGH] + df[mjp.LOW]) / 2 + (f * df[atr])
    df['Lower Basic'] = (df[mjp.HIGH] + df[mjp.LOW]) / 2 - (f * df[atr])
    df['Upper Band'] = df['Upper Basic']
    df['Lower Band'] = df['Lower Basic']
    for i in range(n, len(df)):
        if df['Close'][i - 1] <= df['Upper Band'][i - 1]:
            df.loc[i, 'Upper Band'] = min(df['Upper Basic'][i], df['Upper Band'][i - 1])
        else:
            df.loc[i, 'Upper Band'] = df['Upper Basic'][i]
    for i in range(n, len(df)):
        if df['Close'][i - 1] >= df['Lower Band'][i - 1]:
            df.loc[i, 'Lower Band'] = max(df['Lower Basic'][i], df['Lower Band'][i - 1])
        else:
            df.loc[i, 'Lower Band'] = df['Lower Basic'][i]

    df['SuperTrend'] = np.nan

    for i in df['SuperTrend']:
        if df['Close'][n - 1] <= df['Upper Band'][n - 1]:
            df.loc[n - 1, 'SuperTrend'] = df['Upper Band'][n - 1]
        elif df['Close'][n - 1] > df['Upper Band'][i]:
            df.loc[n - 1, 'SuperTrend'] = df['Lower Band'][n - 1]
    for i in range(n, len(df)):
        if df['SuperTrend'][i - 1] == df['Upper Band'][i - 1] and df['Close'][i] <= df['Upper Band'][i]:
            df.loc[i, 'SuperTrend'] = df['Upper Band'][i]
        elif df['SuperTrend'][i - 1] == df['Upper Band'][i - 1] and df['Close'][i] >= df['Upper Band'][i]:
            df.loc[i, 'SuperTrend'] = df['Lower Band'][i]
        elif df['SuperTrend'][i - 1] == df['Lower Band'][i - 1] and df['Close'][i] >= df['Lower Band'][i]:
            df.loc[i, 'SuperTrend'] = df['Lower Band'][i]
        elif df['SuperTrend'][i - 1] == df['Lower Band'][i - 1] and df['Close'][i] <= df['Lower Band'][i]:
            df.loc[i, 'SuperTrend'] = df['Upper Band'][i]
    df['SuperTrend'] = df['SuperTrend'].apply(lambda x: round(x, 2))
    return df


# df = indicator.moving_average(df,8)

# FACTOR1 = 7
# MULTIPLIER1 = 2
# super_name_1 = 'SuperTrend_'+str(FACTOR1)
#
# df = indicator.average_true_range(df,FACTOR1)
# df = indicator.ST(df,FACTOR1,MULTIPLIER1)
# df = indicator.average_true_range(df,12)
# df = indicator.ST(df,12,4)
# df = indicator.trix(df,15)

#close = df[mjp.CLOSE].iloc[-1]
# print("ram", close)
#
#supertrend = int(df[mjp.SUPERTREND].iloc[-1])
# print("super ", int(supertrend))
# print("ram", close > int(supertrend))
#df = indicator.vortex_indicator(df,7)
# print(df)
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

pd.set_option('display.expand_frame_repr', False)

live_df = pd.read_csv("D://10MINTESTING.csv")

live_df["Date"] = pd.to_datetime(live_df["Date"])
mask = (live_df['Date'] > "2018-12-1")


live_df = live_df[mask]
#data.reset_index(inplace = True)
live_df.reset_index(inplace=True)
live_df["Smooth"] = pd.Series(smoothTriangle(live_df[mjp.CLOSE],8))
print(live_df)
FACTOR1 = 7
MULTIPLIER1 = 2
super_name_1 = 'SuperTrend_'+str(FACTOR1)
live_df = indicator.average_true_range(live_df,FACTOR1)
live_df = indicator.ST(live_df, FACTOR1, MULTIPLIER1)

FACTOR2 = 13
MULTIPLIER2 = 5
super_name_2 = 'SuperTrend_' + str(FACTOR2)
live_df = indicator.average_true_range(live_df, FACTOR2)
live_df = indicator.ST(live_df, FACTOR2, MULTIPLIER2)

live_df = live_df[[mjp.CLOSE, super_name_1,super_name_2]]


for idx in range(21,len(live_df.index)):
    #super1 = int(df.loc[idx, super_name_1])
    close = int(live_df.loc[idx, mjp.CLOSE])
    supertrend1 = int(live_df.loc[idx, super_name_1])
    supertrend2 = int(live_df.loc[idx, super_name_2])
    print("close: {}, supertrend1: {},supertrend2: {} ".format(close,supertrend1,supertrend2))
    print("supertrend2 > supertrend1  ====>", supertrend2 > supertrend1)
    print("close > supertrend1  ====>", close > supertrend1)
    #input = input("Enter to continue.....")
    if supertrend1 > supertrend2:
        if supertrend1 > close and BUY_FLAG:
            # code to cover short
            print("%%%%%%%%%%%%%%%%%%%%%%%%SHORT COVER%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            BUY_FLAG = False
            SELL_FLAG = True
        elif close > supertrend1 and not BUY_FLAG:
            # code to fresh buy
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%BUY%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            BUY_FLAG = True

    else:
        if close > supertrend1 and SELL_FLAG:
            # code to cover long
            print("%%%%%%%%%%%%%%%%%%%%%%%%LONG COVER%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            SELL_FLAG = False
            BUY_FLAG = True

        elif supertrend1 > close and not SELL_FLAG:
            # code to fresh sell
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%SELL%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            SELL_FLAG = True

print("profit===>", profit)
msg += "profit===>{}".format(profit)
# print(live_df.tail())
if SEND_MAIL_FLAG:
    server.sendmail("radharani1306@gmail.com", "pooritrading13@gmail.com", msg)

    # #print("super===>", df.loc[idx,"SuperTrend"]," Close===>",df.loc[idx,"Close"])
    # super1 =int( df.loc[idx,super_name_1])
    # #superbig = int(df.loc[idx, "SuperTrend_12"])
    # close = df.loc[idx,mjp.CLOSE]
    # #vortex = df.loc[idx, "Trix_15"]
    # vortex = df.loc[idx, "Trix_15"]
    # date = df.loc[idx,mjp.DATE]
    # if vortex > 0 and close > super1:        #For Buy purpose
    #     if sell_price != 0 and SELL_FLAG:
    #         buy_price = close
    #         profit += ((sell_price - buy_price) * 100 - 200)
    #         sell_price = 0
    #         BUY_FLAG = True
    #         SELL_FLAG = False
    #         if PRINT_FLAG:
    #             dat = input("At {} bought @{} and Supertrend @{} and profit @{}......".format(date,close, super1,profit))
    #         msg += "At {} bought @{} and Supertrend @{} and profit @{}......\n".format(date,close, super1,profit)
    #     elif not BUY_FLAG:
    #         buy_price = close
    #         BUY_FLAG = True
    #         SELL_FLAG = False
    #         if PRINT_FLAG:
    #             dat = input("At {} buy @{} and Supertrend @{}......".format(date,close,super1))
    #         msg += "At {} buy @{} and Supertrend @{}......".format(date,close,super1)
    #
    #
    # elif  vortex < 0 and close < super1:                    #For Sell purpose
    #     if buy_price != 0 and BUY_FLAG:
    #         sell_price = close
    #         profit += ((sell_price - buy_price) * 100 - 200)
    #         buy_price = 0
    #         SELL_FLAG = True
    #         BUY_FLAG = False
    #         if PRINT_FLAG:
    #             dat = input("At {} sold @{} and Supertrend @{} and profit @{}......".format(date,close, super1,profit))
    #         msg += "At {} sold @{} and Supertrend @{} and profit @{}......".format(date,close, super1,profit)
    #     elif not SELL_FLAG:
    #         sell_price = close
    #         SELL_FLAG = True
    #         BUY_FLAG = False
    #         if PRINT_FLAG:
    #             dat = input("At {} sell@ {} and Supertrend @ {}......".format(date,close,super1))
    #         msg += "At {} sell@ {} and Supertrend @ {}......".format(date,close,super1)


#
# account_sid = 'ACb224d959b76e603e472e611824539816'
# auth_token = '322c46a2adf6b9a3b4660e0d11d26544'
# URL = 'http://www.way2sms.com/api/v1/sendCampaign'
#
# # get request
# def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
#   req_params = {
#   'apikey':apiKey,
#   'secret':secretKey,
#   'usetype':"stage",
#   'phone': +919700125459,
#   'message':textMessage,
#   'senderid':+919700715602
#   }
#   return requests.post(reqUrl, req_params)
#
# # get response
# response = sendPostRequest(URL, 'provided-api-key', 'provided-secret', 'prod/stage', 'valid-to-mobile', 'active-sender-id', 'message-text' )
# """
#   Note:-
#     you must provide apikey, secretkey, usetype, mobile, senderid and message values
#     and then requst to api
# """
# # print response if you want
# print (response.text)

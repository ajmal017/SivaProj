import pandas as pd
import numpy as np
import KuberIndicators as indicator
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc

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


pd.set_option('display.expand_frame_repr', False)
df=pd.read_csv("D://10MINTESTING.csv")


FACTOR1 = 144
MULTIPLIER1 = 3
super_name_1 = 'SuperTrend_'+str(FACTOR1)
df = df.tail(180)
df.reset_index(inplace=True)

df = indicator.average_true_range(df,FACTOR1)
df = indicator.ST(df,FACTOR1, MULTIPLIER1)
df["SuperTrend_144"] = df["SuperTrend_144"].apply(lambda x: round(x,2))
df["new"] = ((df["High"]+df["Low"]+df["Close"])/3).apply(lambda x: int(x))
df["EMA_13"] = pd.Series(indicator.EMA(df["new"],13)).apply(lambda x: round(x,2))
df["EMA_34"] = pd.Series(indicator.EMA(df["new"],34)).apply(lambda x: round(x,2))
df.dropna(inplace=True) # drop NA values from Dataframe
#df = df[["Date","open","high","low","Close","SuperTrend_144","EMA_13","EMA_34"]]
df.set_index("Date",inplace=True)
df = df.tail(50)
#print(df)


fig,ax = plt.subplots(1,1,figsize = (20,9)) #share x axis and set a figure size

#ax.plot(df.index, df.Close,linewidth=4) # plot Close with index on x-axis with a line thickness of 4
# ax.plot(df.index, df.SuperTrend_144) # plot Lead Span A with index on the shared x-axis
# ax.plot(df.index, df.EMA_13) # plot EMA 13 with index on the shared x-axis
# ax.plot(df.index, df.EMA_34) # plot EMA 34 with index on the shared x-axis
plt.xticks(rotation = 45)
candlestick_ohlc(ax, [df.Open, df.High, df.Low, df.Close], width=1, colorup='green', colordown='red')
#ax.plot(df.Date,df.EMA_13)
# plt.legend(loc=0) #Let matplotlib choose best location for legend
# plt.grid() # display the major grid
#plt.show() # Finally display the plot


# CL_period = 9 # length of Tenkan Sen or Conversion Line
# BL_period = 26 # length of Kijun Sen or Base Line
# Lead_span_B_period = 52 # length of Senkou Sen B or Leading Span B
# Lag_span_period = 26 # length of Chikou Span or Lagging Span
#
#
# df['Conv_line'] = (df.High.shift(CL_period)+df.Low.shift(CL_period))/2
# df['Base_line'] = (df.High.shift(BL_period)+df.Low.shift(BL_period))/2
# df['Lead_span_A'] = (df['Conv_line'] + df['Base_line'])/2
# df['Lead_span_B'] = (df.High.shift(Lead_span_B_period)+df.Low.shift(Lead_span_B_period))/2
# df['Lagging_span'] = df.Close.shift(Lag_span_period)
# df.dropna(inplace=True) # drop NA values from Dataframe
#
# df = df.tail(30)
#
# # plot the data using matplotlib's functionality
# #add figure and axis objects
# fig,ax = plt.subplots(1,1,sharex=True,figsize = (20,9)) #share x axis and set a figure size
# ax.plot(df.index, df.Close,linewidth=4) # plot Close with index on x-axis with a line thickness of 4
# ax.plot(df.index, df.Lead_span_A) # plot Lead Span A with index on the shared x-axis
# ax.plot(df.index, df.Lead_span_B) # plot Lead Span B with index on the sahred x-axis
# ax.plot(df.index, df.Conv_line) # plot ConversionLine with index on the sahred x-axis
# ax.plot(df.index, df.Base_line) # plot BaseLine with index on the sahred x-axis
# ax.plot(df.index, df.Lagging_span) # plot LaggingSpan with index on the sahred x-axis
#
# # use the fill_between call of ax object to specify where to fill the chosen color
# # pay attention to the conditions specified in the fill_between call
# ax.fill_between(df.index,df.Lead_span_A,df.Lead_span_B,where = df.Lead_span_A >= df.Lead_span_B, color = 'lightgreen')
# ax.fill_between(df.index,df.Lead_span_A,df.Lead_span_B,where = df.Lead_span_A < df.Lead_span_B, color = 'lightcoral')

# plt.legend(loc=0) #Let matplotlib choose best location for legend
# plt.grid() # display the major grid
# plt.show() # Finally display the plot
# print(df)
# live_df = pd.read_csv("D://10MINTESTING.csv",parse_dates=True)
#
# #live_df["Date"] = pd.to_datetime(live_df["Date"])
# mask = (live_df['Date'] > "2018-12-1")
#
#
# live_df = live_df[mask]
# #data.reset_index(inplace = True)
# live_df.reset_index(inplace=True)
# #live_df["Smooth"] = pd.Series(smoothTriangle(live_df["Close"],8)).apply(lambda x: round(x,2))
# #live_df["Smooth_another"] = live_df["Close"].rolling(window=8, win_type='triang').mean().apply(lambda x: round(x,2))
# live_df["blackmanharris"] = live_df["Close"].rolling(window=3, win_type='blackmanharris').mean()
# live_df = live_df[pd.notnull(live_df['blackmanharris'])]
# live_df["blackmanharris"] = live_df["blackmanharris"].apply(lambda x: int(x))
# live_df.reset_index(inplace=True)
# live_df = live_df[['Date','Open','High','Low','Close','blackmanharris']]
# #print(live_df)
# FACTOR1 = 7
# MULTIPLIER1 = 2
# super_name_1 = 'SuperTrend_'+str(FACTOR1)
# live_df = indicator.custom_atr(live_df,"blackmanharris",FACTOR1)
# live_df = indicator.custom_supertrend(live_df,"blackmanharris" ,FACTOR1, MULTIPLIER1)
#
# #print(live_df)
#
# import matplotlib.pyplot as plt
#
# #here 'df' signifies the financial data which we imported earlier from Yahoo Finance
# #plt.plot(live_df[super_name_1])
# live_df = live_df.tail(20)
# plt.plot(live_df['Date'], live_df[['Close',super_name_1]], color = 'blue', label = 'SuperTrend')
# #We can give a title to our graph which in this case is 'Plotting Data'
# plt.title('Plotting data')
#
# #Used to label x-axis
# plt.xlabel('Time')
#
# #Used to label y-axis
# plt.ylabel('Price')
# plt.show()
import logging
from threading import Thread
import KuberIndicators as indicator
from KuberUtils import KuberUtils
import pandas as pd
import KuberConfig as mjp
from upstox_api.api import *

pd.set_option('display.expand_frame_repr', False)

class KuberTradeThread(Thread):

    def __init__(self,upstoxobj,ohlc_df):
        Thread.__init__(self)
        self.upstoxobj = upstoxobj
        self.live_df = ohlc_df

    def placeOrder(self,side,qty = 1):
        self.upstoxobj.place_order(
            side,  # transaction_type
            self.upstoxobj.get_instrument_by_symbol(mjp.FUTURE_EXCHANGE, mjp.FUTURE_CONTRACT),  # instrument
            qty,  # quantity
            OrderType.Market,  # order_type
            ProductType.Delivery,  # product_type
            0.0,  # price
            None,  # trigger_price
            0,  # disclosed_quantity
            DurationType.DAY, # duration
            None,  # stop_loss
            None,  # square_off
            None  # trailing_ticks
        )

    def run(self):
        FACTOR1 = 144
        MULTIPLIER1 = 3
        super_name_1 = 'SuperTrend_' + str(FACTOR1)
        ema13 = "EMA_13"
        ema34 = "EMA_34"
        self.live_df = indicator.average_true_range(self.live_df, FACTOR1)
        self.live_df = indicator.ST(self.live_df, FACTOR1, MULTIPLIER1)
        self.live_df["new"] = ((self.live_df[mjp.HIGH] + self.live_df[mjp.LOW] + self.live_df[mjp.CLOSE]) / 3).apply(lambda x: int(x))
        self.live_df[ema13] = pd.Series(indicator.EMA(self.live_df["new"], 13)).apply(lambda x: round(x, 2))
        self.live_df[ema34] = pd.Series(indicator.EMA(self.live_df["new"], 34)).apply(lambda x: round(x, 2))
        self.live_df.dropna(inplace=True)  # drop NA values from Dataframe

        self.live_df = self.live_df[[mjp.CLOSE,super_name_1,ema13,ema34]]
        print(self.live_df.tail())
        print("*" * 20)
        return  #This is Temporary return statement to skip below code to execute

        kuber_utils = KuberUtils(self.upstoxobj)
        BUY_FLAG = kuber_utils.CheckPositionBuy(mjp.FUTURE_CONTRACT)
        SELL_FLAG = kuber_utils.CheckPositionSell(mjp.FUTURE_CONTRACT)
        close = self.live_df[mjp.CLOSE].iloc[-1]
        supertrend1 = int(self.live_df[super_name_1].iloc[-1])

        print("close > supertrend1  ====>",close > supertrend1 )


        if close > supertrend1:
            if (SELL_FLAG and not BUY_FLAG):
                #code to cover short
                print("%%%%%%%%%%%%%%%%%%%%%%%%SHORT COVER%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                # order_update = self.placeOrder(TransactionType.Buy,qty = 2)
                # print("in cover short==>",order_update)
            elif (BUY_FLAG):
                #code to fresh buy
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%BUY%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                # order_update = self.placeOrder(TransactionType.Buy, qty=1)
                # print("in fresh buy==>", order_update)
        else:
            if (BUY_FLAG and not SELL_FLAG):
                # code to cover Long
                print("%%%%%%%%%%%%%%%%%%%%COVER LONG%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                # order_update = self.placeOrder(TransactionType.Sell, qty=2)
                # print("in cover long==>", order_update)
            elif (SELL_FLAG):
                # code to fresh sell
                print("%%%%%%%%%%%%%%%%%%%%%%%%%SELL%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                # order_update = self.placeOrder(TransactionType.Sell, qty=1)
                # print("in fresh sell==>", order_update)

        print("=" * 20)
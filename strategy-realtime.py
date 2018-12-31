from upstox_api.api import Upstox,  OHLCInterval, OrderType, ProductType, DurationType, \
    LiveFeedType
import KuberConfig as mjp
import time
from datetime import datetime
from KuberHoliday import KuberHoliday
import pandas as pd
from mythreads.KuberTradeThread import KuberTradeThread

class UpstoxMainPrg():


    def __init__(self,period):
        start = time.time()

        self.ohlc_df = None
        self.period = period
        self.apiKey = mjp.API_KEY
        self.accessCode = mjp.ACCESS_CODE
        self.timestamp = mjp.TIME_STAMP
        self.ltp = mjp.LTP
        self.vtt = "vtt"
        self.FIRST_FLAG = True
        self.df_date = None
        self.data_list = None
        self.vol_data = 0.0

        t_end = None
        #self.live_df = pd.DataFrame()

        # Scrip details
        self.fut_exchange = mjp.FUTURE_EXCHANGE
        self.fut_contract = mjp.FUTURE_CONTRACT


        # Create the UpstoxAPI object bound to your API key
        self.upstoxAPI = Upstox(self.apiKey, self.accessCode)
        self.upstoxAPI.get_master_contract(mjp.FUTURE_EXCHANGE)
        print("Connected Successfully............")
        self.SCRIP = self.upstoxAPI.get_instrument_by_symbol(self.fut_exchange, self.fut_contract)
        self.ohlc_list = self.pre_process(self.upstoxAPI,self.SCRIP)
        # print("Time taken in init method:: ", (time.time() - start),"<===")

    def pre_process(self,myupstox,instrument):
        ohlc_start_date = datetime.strptime(mjp.END_DATE, mjp.DATE_FORMAT).date()
        ohlc_end_date = datetime.strptime(mjp.END_DATE, mjp.DATE_FORMAT).date()
        ohlc_interval = OHLCInterval.Minute_1

        self.ohlc_df = pd.DataFrame(
            myupstox.get_ohlc(instrument, ohlc_interval, ohlc_start_date, ohlc_end_date))  # OHLC DATAFRAME
        col_names = [mjp.CLOSE, mjp.CP, mjp.HIGH, mjp.LOW, mjp.OPEN, mjp.DATE, mjp.VOLUME]
        self.ohlc_df.columns = col_names
        pd.set_option('display.expand_frame_repr', False)
        pd.options.display.max_rows = 999
        pd.options.mode.chained_assignment = None

        # col_names = [mjp.CLOSE, mjp.CP, mjp.HIGH, mjp.LOW, mjp.OPEN, mjp.DATE, mjp.VOLUME]
        # self.ohlc_df.columns = col_names

        self.ohlc_df = self.ohlc_df[[mjp.DATE, mjp.OPEN, mjp.HIGH, mjp.LOW, mjp.CLOSE,mjp.VOLUME]]
        self.ohlc_df[mjp.DATE] = pd.to_datetime(self.ohlc_df[mjp.DATE].apply(lambda x: datetime.fromtimestamp(x / 1000)))
        # print(ohlc_df)

        self.ohlc_df.set_index(mjp.DATE, inplace=True)
        self.ohlc_df.sort_index(inplace=True)
        ohlc_df = self.ohlc_df[self.ohlc_df.index.dayofweek < 5]  # Here OHLC DATAFRAME will be without weekends

        self.ohlc_df.reset_index(inplace=True)  # to remove mjp.DATE index after we remove weekends

        holiday_mask_2018 = self.ohlc_df[mjp.DATE].apply(lambda x: KuberHoliday().holidays_2018_mask(x))
        self.ohlc_df = self.ohlc_df[holiday_mask_2018]  # Final OHLC DATAFRAME will be without weekends,Holidays in that year7
        print(self.ohlc_df.tail(30))
        return self.ohlc_df

    def set_ltp(self,ltp,vtt,timestamp):
        if(self.FIRST_FLAG):
            # print("Ram==>",datetime.now())
            # print("Anji==>",datetime.fromtimestamp(timestamp/1000))
            self.df_date = datetime.now()
            self.data_list = []

            self.t_end = time.time() + 60 * self.period
            self.FIRST_FLAG = False

        if time.time() <= self.t_end:
            self.data_list.append(ltp)
            if self.vol_data ==0.0:
                self.vol_data = vtt
            elif vtt > self.vol_data :
                self.vol_data = vtt - self.vol_data

        else:


            dummydf = pd.DataFrame(
                    {mjp.DATE : self.df_date,
                     mjp.OPEN : self.data_list[0],
                     mjp.HIGH : max(self.data_list),
                     mjp.LOW : min(self.data_list),
                     mjp.CLOSE : self.data_list[-1],
                     mjp.VOLUME:self.vol_data},
                     index=range(1))

            live_df = self.ohlc_df.append(dummydf, ignore_index=True)

            my_thread = KuberTradeThread(self.upstoxAPI,live_df)
            my_thread.daemon = False  # Daemonize thread
            my_thread.start()  # Start the execution
            self.df_date = None
            data_list = []
            self.t_end = None
            self.vol_data = 0.0
            self.FIRST_FLAG = True
            print(live_df.tail(),"  Left else BLOCK @:: ", time.time(), "<===")



    def event_handler_quote_update(self,message):
        #print(message[self.timestamp])
        self.set_ltp(int(message[self.ltp]),float(message[self.vtt]),int(message[self.timestamp]))

    def event_handler_order_update(self,message):
        print("Order Update:" + str(datetime.now()))
        print(message)


    def event_handler_trade_update(self,message):
        print("Trade Update:" + str(datetime.now()))
        print(message)


    def event_handler_error(self,err):
        print("ERROR" + str(datetime.now()))
        print(err)


    def event_handler_socket_disconnect(self):
        print("SOCKET DISCONNECTED" + str(datetime.now()))


    def placeOrder(self,side):
        self.upstoxAPI.place_order(
            side,  # transaction_type
            self.SCRIP,  # instrument
            1,  # quantity
            OrderType.Market,  # order_type
            ProductType.Intraday,  # product_type
            0.0,  # price
            None,  # trigger_price
            0,  # disclosed_quantity
            DurationType.DAY,  # duration
            None,  # stop_loss
            None,  # square_off
            None  # trailing_ticks
        )


    def socket_connect(self,hours,minutes):
        print("Adding Socket Listeners")
        self.upstoxAPI.set_on_quote_update(self.event_handler_quote_update)
        self.upstoxAPI.set_on_order_update(self.event_handler_order_update)
        self.upstoxAPI.set_on_trade_update(self.event_handler_trade_update)
        self.upstoxAPI.set_on_error(self.event_handler_error)
        self.upstoxAPI.set_on_disconnect(self.event_handler_socket_disconnect)

        print("Suscribing to: " + self.SCRIP[4])

        print(self.SCRIP)
        # self.upstoxAPI.unsubscribe(self.SCRIP, LiveFeedType.LTP)
        # self.upstoxAPI.subscribe(self.SCRIP, LiveFeedType.LTP)
        self.upstoxAPI.unsubscribe(self.SCRIP, LiveFeedType.Full)
        self.upstoxAPI.subscribe(self.SCRIP, LiveFeedType.Full)

        print("Connecting to Socket")
        while_flag = True
        while while_flag:
            if (datetime.now() >= datetime.now().replace(hour=hours, minute=minutes, second=00, microsecond=0)):
                self.upstoxAPI.start_websocket(False)
                #while_flag = False



hours = 15
minutes = 0
interval = 1
upstox = UpstoxMainPrg(interval)
upstox.socket_connect(hours,minutes)

import logging
from upstox_api.api import *
from datetime import datetime
import time
import KuberConfig as mjp
import pandas as pd
from mythreads.KuberTradeThread import KuberTradeThread


class KuberLiveData():
    def __init__(self,upstoxobj,instrument,ohlc_df):
        self.upstoxobj = upstoxobj
        self.instrument = instrument
        self.ohlc_df = ohlc_df
        logging.info("KuberLiveData object created")

    def get_data(self,period):
        t_end = time.time() + 60 * period
        datalist = []
        print("entered at ====>", datetime.now())
        first_flag=False
        while time.time() < t_end:
            if first_flag:
                time.sleep(0.9)
            ltp_data = None
            try:
                data = self.upstoxobj.get_live_feed(self.instrument, LiveFeedType.LTP)

                ltp_data = data[mjp.LTP]
                #print(ltp_data)
                datalist.append(ltp_data)
                # if temp_ctr < 3:
                #    temp_ctr += 1
                # else:
                #     temp_ctr = 0
                first_flag = True
            except ValueError as valerr:
                print("value error at get_data() in KuberLiveData:: ",valerr)
            except Exception as exc:
                print("Exception at get_data() in KuberLiveData:: ",exc)
        return datalist

    def process_live_data(self,hours,minutes,interval):
        ctr = 0
        bool_flag = False

        self.ohlc_df = self.ohlc_df[[mjp.DATE,mjp.OPEN,mjp.HIGH, mjp.LOW, mjp.CLOSE]]

        while True:
            # if bool_flag:
            #     minutes += interval
            if (bool_flag or (datetime.now() >= datetime.now().replace(hour=hours, minute=minutes, second=00, microsecond=0))):
                candle_time = datetime.now()
                my_thread = None
                data = self.get_data(interval) #code to retrieve live data

                print("exited at ====>", datetime.now())

                live_df = pd.DataFrame(
                    {mjp.DATE:candle_time,mjp.OPEN: data[0], mjp.HIGH: max(data),
                     mjp.LOW: min(data), mjp.CLOSE: data[-1]},
                    index=range(1))

                self.ohlc_df = self.ohlc_df.append(live_df, ignore_index=True)  # Append to last row

                my_thread = KuberTradeThread(self.upstoxobj,self.ohlc_df)
                my_thread.daemon = False  # Daemonize thread
                my_thread.start()  # Start the execution
                bool_flag = True

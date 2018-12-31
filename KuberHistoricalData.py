from datetime import datetime
from KuberHoliday import KuberHoliday
import pandas as pd
import KuberConfig as mjp

class KuberHistoricalData():
    def __init__(self):
        print("")
    # def create_history_data(self,ohlc_df):
    #     col_names = [mjp.CLOSE, mjp.CP, mjp.HIGH, mjp.LOW, mjp.OPEN, mjp.DATE, mjp.VOLUME]
    #     ohlc_df.columns = col_names
    #     ohlc_df = ohlc_df[[mjp.DATE, mjp.OPEN, mjp.HIGH, mjp.LOW, mjp.CLOSE, mjp.CP, mjp.VOLUME]]
    #     ohlc_df[mjp.DATE] = pd.to_datetime(ohlc_df[mjp.DATE].apply(lambda x: datetime.fromtimestamp(x / 1000)))
    #     #print(ohlc_df)
    #     ohlc_df.set_index(mjp.DATE, inplace=True)
    #     ohlc_df.sort_index(inplace=True)
    #     ohlc_df = ohlc_df[ohlc_df.index.dayofweek < 5]  # Here OHLC DATAFRAME will be without weekends
    #
    #     ohlc_df.reset_index(inplace=True)  # to remove mjp.DATE index after we remove weekends
    #
    #     holiday_mask_2018 = ohlc_df[mjp.DATE].apply(lambda x: KuberHoliday().holidays_2018_mask(x))
    #     ohlc_df = ohlc_df[holiday_mask_2018]  # Final OHLC DATAFRAME will be without weekends,Holidays in that year
    #     return ohlc_df

    def create_history_data(self,df,ONE_TIME_FLAG=True):
        # disable chained assignments
        pd.options.mode.chained_assignment = None

        col_names = [mjp.CLOSE, mjp.CP, mjp.HIGH, mjp.LOW, mjp.OPEN, mjp.DATE, mjp.VOLUME]
        df.columns = col_names
        ohlc_df = df[[mjp.DATE, mjp.OPEN, mjp.HIGH, mjp.LOW, mjp.CLOSE]]
        ohlc_df[mjp.DATE] = pd.to_datetime(ohlc_df[mjp.DATE].apply(lambda x: datetime.fromtimestamp(x / 1000)))
        #print(ohlc_df)
        if ONE_TIME_FLAG :
            ohlc_df.set_index(mjp.DATE, inplace=True)
            ohlc_df.sort_index(inplace=True)
            ohlc_df = ohlc_df[ohlc_df.index.dayofweek < 5]  # Here OHLC DATAFRAME will be without weekends

            ohlc_df.reset_index(inplace=True)  # to remove mjp.DATE index after we remove weekends

            holiday_mask_2018 = ohlc_df[mjp.DATE].apply(lambda x: KuberHoliday().holidays_2018_mask(x))
            ohlc_df = ohlc_df[holiday_mask_2018]  # Final OHLC DATAFRAME will be without weekends,Holidays in that year
        return ohlc_df
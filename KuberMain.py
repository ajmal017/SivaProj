import logging
from upstox_api.api import *
from datetime import datetime
from KuberUtils import KuberUtils
from KuberHistoricalData import KuberHistoricalData
from KuberLiveData import KuberLiveData
import KuberConfig as mjp
import pandas as pd

Myexchanges = None
Master_contract_flag = False
OHLC_data_flag =False #True
OHLC_data_flag = True
Live_data_flag =False #True
Live_data_flag = True
BACKUP_FLAG = True
BACKUP_FLAG = False
ohlc_df = None

"""
    LOGGING FUNCTIONALITY INITIALIZATION
"""
filename = mjp.LOG_FILE_NAME.format(datetime.now().strftime("%d%b%Y"))
logging.basicConfig(filename=filename,
                    filemode='w',
                    format='%(asctime)s : %(filename)s-%(funcName)s-%(module)s:%(levelname)s:%(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S%p',
                    level=logging.DEBUG)




access_token = mjp.ACCESS_CODE
api_key = mjp.API_KEY

upstoxobj = Upstox (api_key, access_token)
logging.info("Upstox object created successfully")
kuberutil = KuberUtils(upstoxobj)

print (kuberutil.get_profile()) # get profile

balance = kuberutil.get_balance()
if(balance != None):
    print (balance[mjp.COMMODITY][mjp.USED_MARGIN]) # get balance / margin limits

print (kuberutil.get_holdings()) # get holdings
print (kuberutil.get_positions()) # get positions

if(upstoxobj.get_profile() != None):
    Myexchanges = upstoxobj.get_profile()[mjp.EXCHANGES_ENABLED]
    upstoxobj.get_master_contract(mjp.FUTURE_EXCHANGE)
    Master_contract_flag = True

if Master_contract_flag:
    logging.info("Master Contract created successfully")
    instrument = upstoxobj.get_instrument_by_symbol(mjp.FUTURE_EXCHANGE, mjp.FUTURE_CONTRACT)
    """
        **************History Retrieval code Starts Here**************
    """
    data = upstoxobj.get_live_feed(instrument, LiveFeedType.Full)[mjp.LTP]
    if OHLC_data_flag:
        logging.info("Fetching OHLC Data............")
        ohlc_df = None
        ohlc_start_date = datetime.strptime(mjp.START_DATE, mjp.DATE_FORMAT).date()
        ohlc_end_date = datetime.strptime(mjp.END_DATE, mjp.DATE_FORMAT).date()
        ohlc_interval = OHLCInterval.Minute_10

        ohlc_df = pd.DataFrame(
            upstoxobj.get_ohlc(instrument, ohlc_interval, ohlc_start_date, ohlc_end_date))  # OHLC DATAFRAME
        col_names = [mjp.CLOSE, mjp.CP, mjp.HIGH, mjp.LOW, mjp.OPEN, mjp.DATE, mjp.VOLUME]
        ohlc_df.columns = col_names
        pd.set_option('display.expand_frame_repr', False)
        pd.options.display.max_rows = 999
        # print(pd.to_datetime(ohlc_df[mjp.DATE].apply(lambda x: datetime.fromtimestamp(x / 1000))))
        ohlc_df = KuberHistoricalData().create_history_data(ohlc_df)
        logging.info("Fetched OHLC Data Successfully............")
        #print(ohlc_df)
        if BACKUP_FLAG:
            ohlc_df.to_csv('D://10MINTESTING.csv', index=False)


    """
            **************Live Retrieval code Starts Here *************
    """
    if Live_data_flag:
        hours = 18
        minutes = 30
        interval = 10

        logging.info("Fetching Live Data started............")
        kld = KuberLiveData(upstoxobj,instrument,ohlc_df)
        kld.process_live_data(hours,minutes,interval)

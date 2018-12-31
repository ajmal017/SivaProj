import KuberConfig as mjp
"""
Indicators as shown by Peter Bakker at:
https://www.quantopian.com/posts/technical-analysis-indicators-without-talib-code
"""

"""
25-Mar-2018: Fixed syntax to support the newest version of Pandas. Warnings should no longer appear.
             Fixed some bugs regarding min_periods and NaN.
			 If you find any bugs, please report to github.com/palmbook
"""

# Import Built-Ins
import logging

# Import Third-Party
import pandas as pd
import numpy as np

# Import Homebrew

# Init Logging Facilities
log = logging.getLogger(__name__)


def moving_average(df, n):
    """Calculate the moving average for the given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    MA = pd.Series(df[mjp.CLOSE].rolling(n, min_periods=n).mean(), name='MA_' + str(n))
    df = df.join(MA)
    return df

def EMA(values, window):
    weights = np.exp(np.linspace(1., 0., window))
    weights /= weights.sum()
    a = np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a

def exponential_moving_average(df, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    EMA = pd.Series(df[mjp.CLOSE].ewm(span=n, min_periods=n).mean(), name='EMA_' + str(n))
    df = df.join(EMA)
    return df


def momentum(df, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    M = pd.Series(df[mjp.CLOSE].diff(n), name='Momentum_' + str(n))
    df = df.join(M)
    return df


def rate_of_change(df, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    M = df[mjp.CLOSE].diff(n - 1)
    N = df[mjp.CLOSE].shift(n - 1)
    ROC = pd.Series(M / N, name='ROC_' + str(n))
    df = df.join(ROC)
    return df


def average_true_range(df, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        TR = max(df.loc[i + 1, mjp.HIGH], df.loc[i, mjp.CLOSE]) - min(df.loc[i + 1, mjp.LOW], df.loc[i, mjp.CLOSE])
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l)
    ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean(), name='ATR_' + str(n))
    df = df.join(ATR)
    return df


def bollinger_bands(df, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    MA = pd.Series(df[mjp.CLOSE].rolling(n, min_periods=n).mean())
    MSD = pd.Series(df[mjp.CLOSE].rolling(n, min_periods=n).std())
    b1 = 4 * MSD / MA
    B1 = pd.Series(b1, name='BollingerB_' + str(n))
    df = df.join(B1)
    b2 = (df[mjp.CLOSE] - MA + 2 * MSD) / (4 * MSD)
    B2 = pd.Series(b2, name='Bollinger%b_' + str(n))
    df = df.join(B2)
    return df


def ppsr(df):
    """Calculate Pivot Points, Supports and Resistances for given data

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    PP = pd.Series((df[mjp.HIGH] + df[mjp.LOW] + df[mjp.CLOSE]) / 3)
    R1 = pd.Series(2 * PP - df[mjp.LOW])
    S1 = pd.Series(2 * PP - df[mjp.HIGH])
    R2 = pd.Series(PP + df[mjp.HIGH] - df[mjp.LOW])
    S2 = pd.Series(PP - df[mjp.HIGH] + df[mjp.LOW])
    R3 = pd.Series(df[mjp.HIGH] + 2 * (PP - df[mjp.LOW]))
    S3 = pd.Series(df[mjp.LOW] - 2 * (df[mjp.HIGH] - PP))
    psr = {'PP': PP, 'R1': R1, 'S1': S1, 'R2': R2, 'S2': S2, 'R3': R3, 'S3': S3}
    PSR = pd.DataFrame(psr)
    df = df.join(PSR)
    return df


def stochastic_oscillator_k(df):
    """Calculate stochastic oscillator %K for given data.

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    SOk = pd.Series((df[mjp.CLOSE] - df[mjp.LOW]) / (df[mjp.HIGH] - df[mjp.LOW]), name='SO%k')
    df = df.join(SOk)
    return df


def stochastic_oscillator_d(df, n):
    """Calculate stochastic oscillator %D for given data.
    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    SOk = pd.Series((df[mjp.CLOSE] - df[mjp.LOW]) / (df[mjp.HIGH] - df[mjp.LOW]), name='SO%k')
    SOd = pd.Series(SOk.ewm(span=n, min_periods=n).mean(), name='SO%d_' + str(n))
    df = df.join(SOd)
    return df


def trix(df, n):
    """Calculate TRIX for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    EX1 = df[mjp.CLOSE].ewm(span=n, min_periods=n).mean()
    EX2 = EX1.ewm(span=n, min_periods=n).mean()
    EX3 = EX2.ewm(span=n, min_periods=n).mean()
    i = 0
    ROC_l = [np.nan]
    while i + 1 <= df.index[-1]:
        ROC = (EX3[i + 1] - EX3[i]) / EX3[i]
        ROC_l.append(ROC)
        i = i + 1
    Trix = pd.Series(ROC_l, name='Trix_' + str(n))
    df = df.join(Trix)
    return df


def average_directional_movement_index(df, n, n_ADX):
    """Calculate the Average Directional Movement Index for given data.

    :param df: pandas.DataFrame
    :param n:
    :param n_ADX:
    :return: pandas.DataFrame
    """
    i = 0
    UpI = []
    DoI = []
    while i + 1 <= df.index[-1]:
        UpMove = df.loc[i + 1, mjp.HIGH] - df.loc[i, mjp.HIGH]
        DoMove = df.loc[i, mjp.LOW] - df.loc[i + 1, mjp.LOW]
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        TR = max(df.loc[i + 1, mjp.HIGH], df.loc[i, mjp.CLOSE]) - min(df.loc[i + 1, mjp.LOW], df.loc[i, mjp.CLOSE])
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l)
    ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean())
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean() / ATR)
    NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean() / ATR)
    ADX = pd.Series((abs(PosDI - NegDI) / (PosDI + NegDI)).ewm(span=n_ADX, min_periods=n_ADX).mean(),
                    name='ADX_' + str(n) + '_' + str(n_ADX))
    df = df.join(ADX)
    return df


def macd(df, n_fast, n_slow):
    """Calculate MACD, MACD Signal and MACD difference

    :param df: pandas.DataFrame
    :param n_fast:
    :param n_slow:
    :return: pandas.DataFrame
    """
    EMAfast = pd.Series(df[mjp.CLOSE].ewm(span=n_fast, min_periods=n_slow).mean())
    EMAslow = pd.Series(df[mjp.CLOSE].ewm(span=n_slow, min_periods=n_slow).mean())
    MACD = pd.Series(EMAfast - EMAslow, name='MACD_' + str(n_fast) + '_' + str(n_slow))
    MACDsign = pd.Series(MACD.ewm(span=9, min_periods=9).mean(), name='MACDsign_' + str(n_fast) + '_' + str(n_slow))
    MACDdiff = pd.Series(MACD - MACDsign, name='MACDdiff_' + str(n_fast) + '_' + str(n_slow))
    df = df.join(MACD)
    df = df.join(MACDsign)
    df = df.join(MACDdiff)
    return df


def mass_index(df):
    """Calculate the Mass Index for given data.

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    Range = df[mjp.HIGH] - df[mjp.LOW]
    EX1 = Range.ewm(span=9, min_periods=9).mean()
    EX2 = EX1.ewm(span=9, min_periods=9).mean()
    Mass = EX1 / EX2
    MassI = pd.Series(Mass.rolling(25).sum(), name='Mass Index')
    df = df.join(MassI)
    return df


def vortex_indicator(df, n):
    """Calculate the Vortex Indicator for given data.

    Vortex Indicator described here:
        http://www.vortexindicator.com/VFX_VORTEX.PDF
    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    TR = [0]
    while i < df.index[-1]:
        Range = max(df.loc[i + 1, mjp.HIGH], df.loc[i, mjp.CLOSE]) - min(df.loc[i + 1, mjp.LOW], df.loc[i, mjp.CLOSE])
        TR.append(Range)
        i = i + 1
    i = 0
    VM = [0]
    while i < df.index[-1]:
        Range = abs(df.loc[i + 1, mjp.HIGH] - df.loc[i, mjp.LOW]) - abs(df.loc[i + 1, mjp.LOW] - df.loc[i, mjp.HIGH])
        VM.append(Range)
        i = i + 1
    VI = pd.Series(pd.Series(VM).rolling(n).sum() / pd.Series(TR).rolling(n).sum(), name='Vortex_' + str(n))
    df = df.join(VI)
    return df


def kst_oscillator(df, r1, r2, r3, r4, n1, n2, n3, n4):
    """Calculate KST Oscillator for given data.

    :param df: pandas.DataFrame
    :param r1:
    :param r2:
    :param r3:
    :param r4:
    :param n1:
    :param n2:
    :param n3:
    :param n4:
    :return: pandas.DataFrame
    """
    M = df[mjp.CLOSE].diff(r1 - 1)
    N = df[mjp.CLOSE].shift(r1 - 1)
    ROC1 = M / N
    M = df[mjp.CLOSE].diff(r2 - 1)
    N = df[mjp.CLOSE].shift(r2 - 1)
    ROC2 = M / N
    M = df[mjp.CLOSE].diff(r3 - 1)
    N = df[mjp.CLOSE].shift(r3 - 1)
    ROC3 = M / N
    M = df[mjp.CLOSE].diff(r4 - 1)
    N = df[mjp.CLOSE].shift(r4 - 1)
    ROC4 = M / N
    KST = pd.Series(
        ROC1.rolling(n1).sum() + ROC2.rolling(n2).sum() * 2 + ROC3.rolling(n3).sum() * 3 + ROC4.rolling(n4).sum() * 4,
        name='KST_' + str(r1) + '_' + str(r2) + '_' + str(r3) + '_' + str(r4) + '_' + str(n1) + '_' + str(
            n2) + '_' + str(n3) + '_' + str(n4))
    df = df.join(KST)
    return df


def relative_strength_index(df, n):
    """Calculate Relative Strength Index(RSI) for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    UpI = [0]
    DoI = [0]
    while i + 1 <= df.index[-1]:
        UpMove = df.loc[i + 1, mjp.HIGH] - df.loc[i, mjp.HIGH]
        DoMove = df.loc[i, mjp.LOW] - df.loc[i + 1, mjp.LOW]
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean())
    NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean())
    RSI = pd.Series(PosDI / (PosDI + NegDI), name='RSI_' + str(n))
    df = df.join(RSI)
    return df


def true_strength_index(df, r, s):
    """Calculate True Strength Index (TSI) for given data.

    :param df: pandas.DataFrame
    :param r:
    :param s:
    :return: pandas.DataFrame
    """
    M = pd.Series(df[mjp.CLOSE].diff(1))
    aM = abs(M)
    EMA1 = pd.Series(M.ewm(span=r, min_periods=r).mean())
    aEMA1 = pd.Series(aM.ewm(span=r, min_periods=r).mean())
    EMA2 = pd.Series(EMA1.ewm(span=s, min_periods=s).mean())
    aEMA2 = pd.Series(aEMA1.ewm(span=s, min_periods=s).mean())
    TSI = pd.Series(EMA2 / aEMA2, name='TSI_' + str(r) + '_' + str(s))
    df = df.join(TSI)
    return df


def accumulation_distribution(df, n):
    """Calculate Accumulation/Distribution for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    ad = (2 * df[mjp.CLOSE] - df[mjp.HIGH] - df[mjp.LOW]) / (df[mjp.HIGH] - df[mjp.LOW]) * df['Volume']
    M = ad.diff(n - 1)
    N = ad.shift(n - 1)
    ROC = M / N
    AD = pd.Series(ROC, name='Acc/Dist_ROC_' + str(n))
    df = df.join(AD)
    return df


def chaikin_oscillator(df):
    """Calculate Chaikin Oscillator for given data.

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    ad = (2 * df[mjp.CLOSE] - df[mjp.HIGH] - df[mjp.LOW]) / (df[mjp.HIGH] - df[mjp.LOW]) * df['Volume']
    Chaikin = pd.Series(ad.ewm(span=3, min_periods=3).mean() - ad.ewm(span=10, min_periods=10).mean(), name='Chaikin')
    df = df.join(Chaikin)
    return df


def money_flow_index(df, n):
    """Calculate Money Flow Index and Ratio for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    PP = (df[mjp.HIGH] + df[mjp.LOW] + df[mjp.CLOSE]) / 3
    i = 0
    PosMF = [0]
    while i < df.index[-1]:
        if PP[i + 1] > PP[i]:
            PosMF.append(PP[i + 1] * df.loc[i + 1, 'Volume'])
        else:
            PosMF.append(0)
        i = i + 1
    PosMF = pd.Series(PosMF)
    TotMF = PP * df['Volume']
    MFR = pd.Series(PosMF / TotMF)
    MFI = pd.Series(MFR.rolling(n, min_periods=n).mean(), name='MFI_' + str(n))
    df = df.join(MFI)
    return df


def on_balance_volume(df, n):
    """Calculate On-Balance Volume for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    OBV = [0]
    while i < df.index[-1]:
        if df.loc[i + 1, mjp.CLOSE] - df.loc[i, mjp.CLOSE] > 0:
            OBV.append(df.loc[i + 1, 'Volume'])
        if df.loc[i + 1, mjp.CLOSE] - df.loc[i, mjp.CLOSE] == 0:
            OBV.append(0)
        if df.loc[i + 1, mjp.CLOSE] - df.loc[i, mjp.CLOSE] < 0:
            OBV.append(-df.loc[i + 1, 'Volume'])
        i = i + 1
    OBV = pd.Series(OBV)
    OBV_ma = pd.Series(OBV.rolling(n, min_periods=n).mean(), name='OBV_' + str(n))
    df = df.join(OBV_ma)
    return df


def force_index(df, n):
    """Calculate Force Index for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    F = pd.Series(df[mjp.CLOSE].diff(n) * df['Volume'].diff(n), name='Force_' + str(n))
    df = df.join(F)
    return df


def ease_of_movement(df, n):
    """Calculate Ease of Movement for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    EoM = (df[mjp.HIGH].diff(1) + df[mjp.LOW].diff(1)) * (df[mjp.HIGH] - df[mjp.LOW]) / (2 * df['Volume'])
    Eom_ma = pd.Series(EoM.rolling(n, min_periods=n).mean(), name='EoM_' + str(n))
    df = df.join(Eom_ma)
    return df


def commodity_channel_index(df, n):
    """Calculate Commodity Channel Index for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    PP = (df[mjp.HIGH] + df[mjp.LOW] + df[mjp.CLOSE]) / 3
    CCI = pd.Series((PP - PP.rolling(n, min_periods=n).mean()) / PP.rolling(n, min_periods=n).std(),
                    name='CCI_' + str(n))
    df = df.join(CCI)
    return df


def coppock_curve(df, n):
    """Calculate Coppock Curve for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    M = df[mjp.CLOSE].diff(int(n * 11 / 10) - 1)
    N = df[mjp.CLOSE].shift(int(n * 11 / 10) - 1)
    ROC1 = M / N
    M = df[mjp.CLOSE].diff(int(n * 14 / 10) - 1)
    N = df[mjp.CLOSE].shift(int(n * 14 / 10) - 1)
    ROC2 = M / N
    Copp = pd.Series((ROC1 + ROC2).ewm(span=n, min_periods=n).mean(), name='Copp_' + str(n))
    df = df.join(Copp)
    return df


def keltner_channel(df, n):
    """Calculate Keltner Channel for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    KelChM = pd.Series(((df[mjp.HIGH] + df[mjp.LOW] + df[mjp.CLOSE]) / 3).rolling(n, min_periods=n).mean(),
                       name='KelChM_' + str(n))
    KelChU = pd.Series(((4 * df[mjp.HIGH] - 2 * df[mjp.LOW] + df[mjp.CLOSE]) / 3).rolling(n, min_periods=n).mean(),
                       name='KelChU_' + str(n))
    KelChD = pd.Series(((-2 * df[mjp.HIGH] + 4 * df[mjp.LOW] + df[mjp.CLOSE]) / 3).rolling(n, min_periods=n).mean(),
                       name='KelChD_' + str(n))
    df = df.join(KelChM)
    df = df.join(KelChU)
    df = df.join(KelChD)
    return df


def ultimate_oscillator(df):
    """Calculate Ultimate Oscillator for given data.

    :param df: pandas.DataFrame
    :return: pandas.DataFrame
    """
    i = 0
    TR_l = [0]
    BP_l = [0]
    while i < df.index[-1]:
        TR = max(df.loc[i + 1, mjp.HIGH], df.loc[i, mjp.CLOSE]) - min(df.loc[i + 1, mjp.LOW], df.loc[i, mjp.CLOSE])
        TR_l.append(TR)
        BP = df.loc[i + 1, mjp.CLOSE] - min(df.loc[i + 1, mjp.LOW], df.loc[i, mjp.CLOSE])
        BP_l.append(BP)
        i = i + 1
    UltO = pd.Series((4 * pd.Series(BP_l).rolling(7).sum() / pd.Series(TR_l).rolling(7).sum()) + (
            2 * pd.Series(BP_l).rolling(14).sum() / pd.Series(TR_l).rolling(14).sum()) + (
                             pd.Series(BP_l).rolling(28).sum() / pd.Series(TR_l).rolling(28).sum()),
                     name='Ultimate_Osc')
    df = df.join(UltO)
    return df


def donchian_channel(df, n):
    """Calculate donchian channel of given pandas data frame.
    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    dc_l = []
    while i < n - 1:
        dc_l.append(0)
        i += 1

    i = 0
    while i + n - 1 < df.index[-1]:
        dc = max(df[mjp.HIGH].ix[i:i + n - 1]) - min(df[mjp.LOW].ix[i:i + n - 1])
        dc_l.append(dc)
        i += 1

    donchian_chan = pd.Series(dc_l, name='Donchian_' + str(n))
    donchian_chan = donchian_chan.shift(n - 1)
    return df.join(donchian_chan)


def standard_deviation(df, n):
    """Calculate Standard Deviation for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    df = df.join(pd.Series(df[mjp.CLOSE].rolling(n, min_periods=n).std(), name='STD_' + str(n)))
    return df


def ST(df,n,f): #df is the dataframe, n is the period, f is the factor; f=3, n=7 are commonly used.
    #Calculation of SuperTrend
 
    atr = 'ATR_' + str(n)
    df['Upper Basic']=(df[mjp.HIGH]+df[mjp.LOW])/2+(f*df[atr])
    df['Lower Basic']=(df[mjp.HIGH]+df[mjp.LOW])/2-(f*df[atr])
    df['Upper Band']=df['Upper Basic']
    df['Lower Band']=df['Lower Basic']
    for i in range(n,len(df)):
        if df['Close'][i-1]<=df['Upper Band'][i-1]:
            df.loc[i,'Upper Band']=min(df['Upper Basic'][i],df['Upper Band'][i-1])
        else:
            df.loc[i,'Upper Band'] =df['Upper Basic'][i]
    for i in range(n,len(df)):
        if df['Close'][i-1]>=df['Lower Band'][i-1]:
            df.loc[i, 'Lower Band'] = max(df['Lower Basic'][i],df['Lower Band'][i-1])
        else:
            df.loc[i, 'Lower Band']=df['Lower Basic'][i]

    supertrend = 'SuperTrend_' + str(n)
    df[supertrend]=np.nan

    for i in df[supertrend]:
        if df['Close'][n-1]<=df['Upper Band'][n-1]:
            df.loc[n-1,supertrend]=df['Upper Band'][n-1]
        elif df['Close'][n-1]>df['Upper Band'][i]:
            df.loc[n - 1, supertrend]=df['Lower Band'][n-1]
    for i in range(n,len(df)):
        if df[supertrend][i-1]==df['Upper Band'][i-1] and df[mjp.CLOSE][i]<=df['Upper Band'][i]:
            df.loc[i,supertrend] = df['Upper Band'][i]
        elif  df[supertrend][i-1]==df['Upper Band'][i-1] and df[mjp.CLOSE][i]>=df['Upper Band'][i]:
            df.loc[i, supertrend]=df['Lower Band'][i]
        elif df[supertrend][i-1]==df['Lower Band'][i-1] and df[mjp.CLOSE][i]>=df['Lower Band'][i]:
            df.loc[i, supertrend]=df['Lower Band'][i]
        elif df[supertrend][i-1]==df['Lower Band'][i-1] and df[mjp.CLOSE][i]<=df['Lower Band'][i]:
            df.loc[i, supertrend]=df['Upper Band'][i]
    df[supertrend] = df[supertrend].apply(lambda x: round(x, 2))
    return df

def VWAP(ohlcv):
    """
    The volume weighted average price (VWAP) is a trading benchmark used especially in pension plans.
    VWAP is calculated by adding up the dollars traded for every transaction (price multiplied by number of shares traded) and then dividing
    by the total shares traded for the day.
    """
    print(ohlcv)
    print(type(ohlcv))
    print(ohlcv[0])
    typical_price = (ohlcv[mjp.HIGH] + ohlcv[mjp.LOW] + ohlcv[mjp.CLOSE]) / 3
    return pd.Series(((ohlcv[mjp.VOLUME] * typical_price.cumsum()) / ohlcv[mjp.VOLUME].cumsum())).apply(lambda x: round(x, 2))

def custom_atr(df,column_name, n):
    """

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    TR_l = [0]
    while i < df.index[-1]:
        TR = max(df.loc[i + 1, mjp.HIGH], df.loc[i, column_name]) - min(df.loc[i + 1, mjp.LOW], df.loc[i, column_name])
        TR_l.append(TR)
        i = i + 1
    TR_s = pd.Series(TR_l)
    ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean(), name='ATR_' + str(n))
    df = df.join(ATR)
    return df


def custom_supertrend(df,column_name, n, f):  # df is the dataframe, n is the period, f is the factor; f=3, n=7 are commonly used.
    # Calculation of SuperTrend

    atr = 'ATR_' + str(n)
    df['Upper Basic'] = (df[mjp.HIGH] + df[mjp.LOW]) / 2 + (f * df[atr])
    df['Lower Basic'] = (df[mjp.HIGH] + df[mjp.LOW]) / 2 - (f * df[atr])
    df['Upper Band'] = df['Upper Basic']
    df['Lower Band'] = df['Lower Basic']
    for i in range(n, len(df)):
        if df[column_name][i - 1] <= df['Upper Band'][i - 1]:
            df.loc[i, 'Upper Band'] = min(df['Upper Basic'][i], df['Upper Band'][i - 1])
        else:
            df.loc[i, 'Upper Band'] = df['Upper Basic'][i]
    for i in range(n, len(df)):
        if df[column_name][i - 1] >= df['Lower Band'][i - 1]:
            df.loc[i, 'Lower Band'] = max(df['Lower Basic'][i], df['Lower Band'][i - 1])
        else:
            df.loc[i, 'Lower Band'] = df['Lower Basic'][i]

    supertrend = 'SuperTrend_' + str(n)
    df[supertrend] = np.nan

    for i in df[supertrend]:
        if df[column_name][n - 1] <= df['Upper Band'][n - 1]:
            df.loc[n - 1, supertrend] = df['Upper Band'][n - 1]
        elif df[column_name][n - 1] > df['Upper Band'][i]:
            df.loc[n - 1, supertrend] = df['Lower Band'][n - 1]
    for i in range(n, len(df)):
        if df[supertrend][i - 1] == df['Upper Band'][i - 1] and df[column_name][i] <= df['Upper Band'][i]:
            df.loc[i, supertrend] = df['Upper Band'][i]
        elif df[supertrend][i - 1] == df['Upper Band'][i - 1] and df[column_name][i] >= df['Upper Band'][i]:
            df.loc[i, supertrend] = df['Lower Band'][i]
        elif df[supertrend][i - 1] == df['Lower Band'][i - 1] and df[column_name][i] >= df['Lower Band'][i]:
            df.loc[i, supertrend] = df['Lower Band'][i]
        elif df[supertrend][i - 1] == df['Lower Band'][i - 1] and df[column_name][i] <= df['Lower Band'][i]:
            df.loc[i, supertrend] = df['Upper Band'][i]
    df[supertrend] = df[supertrend].apply(lambda x: round(x, 2))
    return df

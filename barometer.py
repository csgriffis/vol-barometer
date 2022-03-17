from datetime import datetime
from typing import TypedDict

import pandas as pd
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta


class VolatilityLevels(TypedDict):
    """
    VolatilityLevels defines a dict of volatility levels to categorize volatility
    """
    minimum: float
    moderate: float
    average: float
    elevated: float
    extreme: float


def barometer() -> float:
    """
    barometer retrieves various VIX data to calculate the percentile rank of crossovers
    :return: float most recent barometer value
    """
    # set helpful date values
    three_years_ago = datetime.now() - relativedelta(years=3)
    today = datetime.now()

    # retrieve VIX9D
    vix9d = pd.read_csv('https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX9D_History.csv')
    vix9d['DATE'] = pd.to_datetime(vix9d['DATE'])
    vix9d = vix9d[['DATE', 'CLOSE']].rename(columns={'CLOSE': 'vix9d'}).set_index('DATE')

    # retrieve VIX3M
    vix3m = pd.read_csv('https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv')
    vix3m['DATE'] = pd.to_datetime(vix3m['DATE'])
    vix3m = vix3m[['DATE', 'CLOSE']].rename(columns={'CLOSE': 'vix3m'}).set_index('DATE')

    # retrieve VIX6M
    vix6m = pd.read_csv('https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX6M_History.csv')
    vix6m['DATE'] = pd.to_datetime(vix6m['DATE'])
    vix6m = vix6m[['DATE', 'CLOSE']].rename(columns={'CLOSE': 'vix6m'}).set_index('DATE')

    # retrieve VIX
    vix = pd.read_csv('https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv')
    vix['DATE'] = pd.to_datetime(vix['DATE'])
    vix = vix[['DATE', 'CLOSE']].rename(columns={'CLOSE': 'vix'}).set_index('DATE')

    # retrieve S&P Futures price
    spy_futs = web.DataReader("ES=F", 'yahoo', three_years_ago, today)
    spy_futs = spy_futs[['Adj Close']].rename(columns={'Adj Close': 'es_fut'})

    # retrieve VVIX
    vvix = web.DataReader("^VVIX", 'yahoo', three_years_ago, today)
    vvix = vvix[['Adj Close']].rename(columns={'Adj Close': 'vvix'})

    # join all data into a single dataframe
    df = vix9d.join(vix3m).join(vix6m).join(vix).join(spy_futs).join(vvix)

    # filter all values by date
    df = df.loc[three_years_ago:]

    # perform crossover calculations
    df['vix9d/vix'] = df['vix9d'] / df['vix']
    df['vix/vix3m'] = df['vix'] / df['vix3m']
    df['vix/vix6m'] = df['vix'] / df['vix6m']

    # perform misc calculations
    df['vrp'] = (df['vix'] - df['es_fut'].rolling(5).std()).rolling(5).mean()

    # calculate percentile ranks
    df['vix9d/vix_rank'] = df['vix9d/vix'].rank(pct=True)
    df['vix/vix3m_rank'] = df['vix/vix3m'].rank(pct=True)
    df['vix/vix6m_rank'] = df['vix/vix6m'].rank(pct=True)
    # invert vrp rank to align with high pct = high vol
    df['vrp_rank'] = 1 - df['vrp'].rank(pct=True)
    df['vvix_rank'] = df['vvix'].rank(pct=True)

    # calculate barometer value
    df['barometer'] = (
                              df['vix9d/vix_rank'] +
                              df['vix/vix3m_rank'] +
                              df['vix/vix6m_rank'] +
                              df['vrp_rank'] +
                              df['vvix_rank']
                      ) / 5

    # apply exponential moving average
    df['ewm'] = df['barometer'].ewm(halflife=3).mean()

    # retrieve latest value
    return df['ewm'].iloc[-1]

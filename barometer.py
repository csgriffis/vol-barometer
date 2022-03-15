from datetime import datetime
from typing import TypedDict

import pandas as pd
from dateutil.relativedelta import relativedelta


class VolatilityLevels(TypedDict):
    """
    VolatilityLevels defines a dict of volatility levels to categorize volatility
    """
    minimum: int
    moderate: int
    average: int
    elevated: int
    extreme: int


def barometer() -> float:
    """
    barometer retrieves various VIX data to calculate the percentile rank of crossovers
    :return: float most recent barometer value
    """
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

    # join all data into a single dataframe
    df = vix9d.join(vix3m).join(vix6m).join(vix)

    # filter data to only include previous three years
    three_years_ago = datetime.now() - relativedelta(years=3)
    df = df.loc[three_years_ago:]

    # perform crossover calculations
    df['vix9d/vix'] = df['vix9d'] / df['vix']
    df['vix/vix3m'] = df['vix'] / df['vix3m']
    df['vix/vix6m'] = df['vix'] / df['vix6m']

    # calculate percentile ranks
    df['vix9d/vix_rank'] = df['vix9d/vix'].rank(pct=True)
    df['vix/vix3m_rank'] = df['vix/vix3m'].rank(pct=True)
    df['vix/vix6m_rank'] = df['vix/vix6m'].rank(pct=True)

    # calculate barometer value
    df['barometer'] = ((df['vix9d/vix_rank'] * 3) + (df['vix/vix3m_rank'] * 2) + (df['vix/vix6m_rank'] * 1)) / 6

    # apply exponential moving average
    df['ewm'] = df['barometer'].ewm(halflife=3).mean()

    # retrieve latest value
    return df['ewm'].iloc[-1]

from pathlib import Path

import pandas as pd

from stooqie.models import settings


def get_ticker_df(ticker: str, *, parquet_path: Path = settings.parquet_path) -> pd.DataFrame:
    """
    This function returns the dataframe for the ticker by reading the parquet.
    It assumes that the parquet always HAS data and HAS fresh data.

    Args:
        ticker: Name of the ticker

    Returns: Dataframe containing TickerColumns and HistoricalOffsetColumns with ticker name

    """
    stored_df = pd.read_parquet(parquet_path)
    historical_change_df = stored_df.loc[stored_df["ticker"] == ticker]

    return historical_change_df

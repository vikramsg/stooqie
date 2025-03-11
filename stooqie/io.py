from datetime import datetime
from pathlib import Path

import pandas as pd

from stooqie._ticker import historical_change_from_ticker
from stooqie.models import TickerColumns, settings
from stooqie.utils.log import logger


def _get_historical_change_df_from_stooq(ticker: str) -> pd.DataFrame:
    historical_change_df = historical_change_from_ticker(ticker)

    historical_change_df["ticker"] = ticker

    return historical_change_df


def get_ticker_df(
    ticker: str, *, invalidation_ttl: int = settings.invalidation_ttl, parquet_path: Path = settings.parquet_path
) -> pd.DataFrame:
    """
    This function returns the dataframe for the ticker. By default we only want to read the dataframe from parquet.
    However, the parquet may not always have the correct data.
    The cases where it must intervene is when the ticker data is empty or outdated.

    Args:
        ticker: Name of the ticker

    Returns: Dataframe containing TickerColumns and HistoricalOffsetColumns with ticker name

    """
    stored_df = pd.read_parquet(parquet_path)
    historical_change_df = stored_df.loc[stored_df["ticker"] == ticker]

    if len(historical_change_df) == 0:
        ticker_df = _get_historical_change_df_from_stooq(ticker)
        to_store_df = pd.concat([stored_df, ticker_df])
        to_store_df.to_parquet(settings.parquet_path)

        return ticker_df

    latest_date = pd.to_datetime(historical_change_df[TickerColumns.date]).max()
    # If date is too old, then fetch
    if abs((latest_date - datetime.now()).days) > invalidation_ttl:
        historical_change_df = _get_historical_change_df_from_stooq(ticker)
        logger.debug("Ticker %s cache is too old. Fetching...", ticker)

        # TODO: Also need to update the stored parquet. But should we do that here?

    return historical_change_df

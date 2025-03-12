from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from stooqie._ticker import historical_change_from_ticker
from stooqie.models import TickerColumns, settings
from stooqie.utils.log import logger


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


def _get_tickers_to_update(tickers: list[str], tickers_df: pd.DataFrame, *, invalidation_ttl_days: int) -> list[str]:
    """
    TODO: Write test for this function. Is a bit complicated to follow.

    Args:
        tickers:
        tickers_df:
        invalidation_ttl_days:

    Returns:

    """
    # First find tickers where date is too old
    tickers_max_date_df = tickers_df.groupby(by="ticker")["date"].max().reset_index()
    tickers_to_update_because_of_date = tickers_max_date_df.loc[
        (tickers_max_date_df["date"] < datetime.now() - timedelta(invalidation_ttl_days))
        & (tickers_max_date_df["ticker"].isin(tickers)),
        "ticker",
    ].values

    # Then find tickers with empty data
    tickers_count_df = tickers_df.groupby(by="ticker")["date"].count().reset_index().rename(columns={"date": "count"})
    ticker_count_df_from_tickers = pd.DataFrame(data={"ticker": tickers, "count": [0] * len(tickers)}).astype(
        {"count": int}
    )
    ticker_count_join_df = ticker_count_df_from_tickers.merge(
        tickers_count_df, on="ticker", suffixes=(None, "_right"), how="left"
    )
    ticker_count_filled_df = ticker_count_join_df.fillna(0)
    tickers_to_update_because_of_count = ticker_count_filled_df.loc[
        np.int32(ticker_count_filled_df["count"] + ticker_count_filled_df["count_right"]) == 0, "ticker"
    ].values

    return list(tickers_to_update_because_of_date) + list(tickers_to_update_because_of_count)


def write_historical_tickers(tickers: list[str], *, parquet_path: Path, parquet_invalidation_ttl: int) -> None:
    """
    Write the parquet to parquet_path. By default we will just read the parquet for each ticker and write back.
    The 2 conditions where this is not done and instead we download data and write are
        1. If the ticker data is empty.
        2. If the ticker data is too old.

    Args:
        tickers: All tickers to write data for.
        parquet_path: Path of parquet file. We both read and write to the same file.
        parquet_invalidation_ttl: How old can the data be for a ticker before we redownload.
    """
    # Handle file not existing
    if not parquet_path.exists():
        tickers_df = pd.concat([historical_change_from_ticker(ticker) for ticker in tickers]).drop_duplicates()
        tickers_df.to_parquet(parquet_path)
        return

    # We should just vectorize it. Why are we doing a for loop?
    tickers_df = pd.read_parquet(parquet_path)
    tickers_df["date"] = pd.to_datetime(tickers_df[TickerColumns.date])

    tickers_to_update = _get_tickers_to_update(tickers, tickers_df, invalidation_ttl_days=parquet_invalidation_ttl)

    if not tickers_to_update:
        logger.debug("Parquet does not need to be updated.")
        return

    tickers_list = [historical_change_from_ticker(ticker) for ticker in tickers_to_update]
    tickers_df = pd.concat(tickers_list + [tickers_df]).drop_duplicates()

    logger.debug(f"Writing post processed ticker data to parquet at {parquet_path}.")
    tickers_df.to_parquet(parquet_path)

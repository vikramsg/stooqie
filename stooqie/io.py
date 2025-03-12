from datetime import datetime
from pathlib import Path

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

    # Now handle cases where file exists
    all_tickers = []
    for ticker in tickers:
        # Also handle parquet not existing.
        ticker_df = get_ticker_df(ticker, parquet_path=parquet_path)

        latest_data_date = pd.to_datetime(ticker_df[TickerColumns.date]).max()
        if abs((latest_data_date - datetime.now()).days) > parquet_invalidation_ttl:
            ticker_df = historical_change_from_ticker(ticker)

        if len(ticker_df) == 0:
            ticker_df = historical_change_from_ticker(ticker)

        all_tickers.append(ticker_df)
        logger.debug(f"This loop is really, really slow: {ticker}")

    tickers_df = pd.concat(all_tickers).drop_duplicates()

    logger.debug(f"Writing post processed ticker data to parquet at {parquet_path}.")
    tickers_df.to_parquet(parquet_path)

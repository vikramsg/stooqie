import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from stooqie.models import TickerColumns

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s")
logger = logging.getLogger()


@dataclass
class HistoricalOffsetColumn:
    """
    Dataclass to keep track of all historical offset columns we will add to the stocks parquet

    Attributes:
        column_name: Name of column
        years: Number of years offset. Note that by offset we always mean going back
        months: num of months
        days: num of days
    """

    column_name: str
    years: int
    months: int
    days: int


class HistoricalOffsetColumns(HistoricalOffsetColumn, Enum):
    """
    Columns in the Stock that we want to add for doing historical change tracking
    """

    one = "offset_one", 1, 0, 0
    five = "offset_five", 5, 0, 0
    ten = "offset_ten", 10, 0, 0
    twenty = "offset_twenty", 20, 0, 0

    def __repr__(self) -> str:
        return self.value


def _get_historical_data(ticker: str) -> pd.DataFrame:
    """
    Fetch historical stock data for a given ticker from Stooq and return it as a DataFrame.
    """
    url = f"https://stooq.com/q/d/l/?s={ticker}&i=d"
    logging.info(f"Fetching data for ticker: {ticker} from url: {url}.")
    response = requests.get(url)

    csv_data = StringIO(response.text)
    ticker_df = pd.read_csv(csv_data)

    logging.debug("Response: %s", response)
    return ticker_df


def _series_with_nearest_date_for_offset(df: pd.DataFrame, date_column: str, offset: pd.DateOffset) -> pd.Series:
    """
    For a given offset, we will not necessarily find the exact matching date with offset.
    So we need to find the nearest date.
    We of course need to also deal with the fact that the offset may not exist at all.
    """
    df[date_column] = pd.to_datetime(df[date_column])
    series_with_date_offset = df[date_column] - offset

    df_date = df[date_column]
    nearest_indices = abs(series_with_date_offset.values[:, None] - df_date.values).argmin(axis=1)

    nearest_dates = pd.Series(df_date[nearest_indices])

    # Cutoff less than mindates as NaN
    min_date = df[date_column].min()
    nan_indices = np.where(series_with_date_offset < min_date)
    nearest_dates.iloc[nan_indices] = pd.NaT

    return nearest_dates


def historical_change_from_ticker(ticker: str) -> pd.DataFrame:
    ticker_df = _get_historical_data(ticker)
    assert len(ticker_df) > 0, "The given ticker is invalid and has no data."

    ticker_copy_df = ticker_df.copy()

    ticker_copy_df["date"] = pd.to_datetime(ticker_df[TickerColumns.date])
    _historical_change_df = ticker_df.copy()

    # For each column in our historical offsets, compute the offset and store
    for column in HistoricalOffsetColumns:
        nearest_dates_ds = _series_with_nearest_date_for_offset(
            ticker_df,
            date_column=TickerColumns.date,
            offset=pd.DateOffset(years=column.years, months=column.months, days=column.days),
        )

        _historical_change_df["nearest_date"] = nearest_dates_ds.values
        joined_df = _historical_change_df.merge(
            ticker_copy_df, left_on="nearest_date", right_on="date", how="left", suffixes=(None, "_right")
        )

        _historical_change_df[column.column_name] = joined_df[f"{TickerColumns.close}_right"]

    # Retain only the columns we want to have
    historical_change_df: pd.DataFrame = _historical_change_df[
        [column for column in TickerColumns] + [column.column_name for column in HistoricalOffsetColumns]
    ]

    return historical_change_df


def get_ticker_df(ticker: str, *, invalidation_ttl: int, parquet_path: Path) -> pd.DataFrame:
    stored_df = pd.read_parquet(parquet_path)
    historical_change_df = stored_df.loc[stored_df["ticker"] == ticker]

    latest_date = pd.to_datetime(historical_change_df[TickerColumns.date]).max()
    # If date is too old, then fetch
    if abs((latest_date - datetime.now()).days) > invalidation_ttl:
        historical_change_df = historical_change_from_ticker(ticker)

        historical_change_df["ticker"] = ticker
        logger.debug("Ticker %s cache is too old. Fetching...", ticker)

    logger.info("Ticker %s contains %s rows.", ticker, len(historical_change_df))

    return historical_change_df


if __name__ == "__main__":
    logging.info("Starting the application")
    ticker = "AAPL.US"
    historical_change_from_ticker(ticker)

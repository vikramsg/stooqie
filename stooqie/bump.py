from datetime import datetime
from enum import StrEnum
from pathlib import Path

import pandas as pd

from stooqie.models import HistoricalOffsetColumns, TickerColumns


class BumpColumns(StrEnum):
    bump = "bump"
    origin_date = "bump_origin_date"
    origin_value = "bump_origin_value"


def _bump_df_filtered_by_bump_factor(
    bump_df: pd.DataFrame, offset_column: str, offset_years: int, bump_factor: float, *, cutoff_year: int
) -> pd.DataFrame:
    filter_df = bump_df.copy()

    filter_df[BumpColumns.bump] = filter_df[TickerColumns.close] / filter_df[offset_column] - 1
    filter_df[BumpColumns.origin_date] = pd.to_datetime(filter_df[TickerColumns.date]) - pd.DateOffset(
        years=offset_years
    )
    filter_df[BumpColumns.origin_value] = filter_df[offset_column]

    filter_df = filter_df[filter_df[BumpColumns.origin_date].dt.year > cutoff_year]

    return filter_df[filter_df[BumpColumns.bump] > bump_factor].drop_duplicates("ticker", keep="last")[
        [
            "ticker",
            TickerColumns.date,
            TickerColumns.close,
            BumpColumns.origin_date,
            BumpColumns.origin_value,
            BumpColumns.bump,
        ]
    ]  # type: ignore


def _current_value_df(ticker_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each ticker, return its current value.

    Args:
        ticker_df: Ticker df with time series values

    Returns: Dataframe with the most recent value for each ticker in the time series.
    """
    current_df = ticker_df.copy()

    current_values = {}
    current_df["date"] = pd.to_datetime(current_df[TickerColumns.date])
    tickers = pd.unique(ticker_df["ticker"])
    for ticker in tickers:
        ticker_df = current_df.loc[current_df["ticker"] == ticker]
        latest_date = ticker_df.loc[ticker_df["ticker"] == ticker, "date"].max()

        current_values[ticker] = ticker_df.loc[ticker_df["date"] == latest_date, TickerColumns.close].values[0]

    return pd.DataFrame(list(current_values.items()), columns=["ticker", TickerColumns.close])


def bump_dataframe(parquet_file: Path, cutoff_year: int = 2020, *, bump_factor_filter: float = 4) -> pd.DataFrame:
    """
    We want to show tables that have had a more than X bump. We want to provide a starting year,
    and based on that find stocks that would have given more than an X times bump.

    We also want to show the current Close value just to make sure, it hasn't dropped like crazy!

    Args:
        parquet_file:
        bump_factor_filer: How big of a factor should it be to check for a bump. For eg. if set to 5
            then we will only show those rows that have atleast increased by a factor 5.
        num_years_filter: Track only date for the last <num_years_filter> years

    Returns:

    """
    bump_df: pd.DataFrame = pd.read_parquet(parquet_file)

    bump_df["date"] = pd.to_datetime(bump_df[TickerColumns.date])
    bump_df = bump_df[bump_df["date"] > datetime.fromisoformat(f"{cutoff_year}-01-01")]  # type: ignore

    hc_one = HistoricalOffsetColumns.one
    hc_two = HistoricalOffsetColumns.two
    hc_five = HistoricalOffsetColumns.five

    bump_factor_fraction = bump_factor_filter - 1
    big_bumps_df = pd.concat(
        [
            _bump_df_filtered_by_bump_factor(
                bump_df, hc_one.column_name, hc_one.years, bump_factor_fraction, cutoff_year=cutoff_year
            ),
            _bump_df_filtered_by_bump_factor(
                bump_df, hc_two.column_name, hc_two.years, bump_factor_fraction, cutoff_year=cutoff_year
            ),
            _bump_df_filtered_by_bump_factor(
                bump_df, hc_five.column_name, hc_five.years, bump_factor_fraction, cutoff_year=cutoff_year
            ),
        ]
    )

    current_value_df = _current_value_df(bump_df)
    bump_with_current_value_df = big_bumps_df.merge(current_value_df, on="ticker").rename(
        columns={f"{TickerColumns.close}_x": TickerColumns.close, f"{TickerColumns.close}_y": "current_value"}
    )

    return bump_df

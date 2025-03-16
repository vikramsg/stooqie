from datetime import datetime
from enum import StrEnum
from pathlib import Path

import pandas as pd

from stooqie.models import HistoricalOffsetColumns, TickerColumns


class BumpColumns(StrEnum):
    one = "bump_one"
    two = "bump_two"
    five = "bump_five"


def _rows_with_bump_over_column(bump_df: pd.DataFrame, column: str, bump_factor: float) -> pd.DataFrame:
    return bump_df[bump_df[column] > bump_factor].drop_duplicates("ticker", keep="last")  # type: ignore


def bump_dataframe(parquet_file: Path, cutoff_year: int = 2020, *, bump_factor_filter: float = 5) -> pd.DataFrame:
    """
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

    bump_df[BumpColumns.one] = bump_df[TickerColumns.close] / bump_df[HistoricalOffsetColumns.one.column_name] - 1
    bump_df[BumpColumns.two] = bump_df[TickerColumns.close] / bump_df[HistoricalOffsetColumns.two.column_name] - 1
    bump_df[BumpColumns.five] = bump_df[TickerColumns.close] / bump_df[HistoricalOffsetColumns.five.column_name] - 1

    bump_factor_fraction = bump_factor_filter - 1
    big_bumps_df = pd.concat(
        [
            _rows_with_bump_over_column(bump_df, BumpColumns.one, bump_factor_fraction),
            _rows_with_bump_over_column(bump_df, BumpColumns.two, bump_factor_fraction),
            _rows_with_bump_over_column(bump_df, BumpColumns.five, bump_factor_fraction),
        ]
    )
    breakpoint()

    return bump_df


def bump_df() -> None:
    """
    What do we want. We want to show tables that have had a more than x bump.
    We want to provide a starting year, and based on that find stocks
    that would have given me more than an X times bump.
    And I also want to show the current Close value just to make sure,
    it hasn't dropped like crazy!
    """

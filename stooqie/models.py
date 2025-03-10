from enum import StrEnum


class TickerColumns(StrEnum):
    """
    Columns in the Ticker that we get from Stooq
    """

    date = "Date"
    open = "Open"
    high = "High"
    low = "Low"
    close = "Close"
    volume = "Volume"

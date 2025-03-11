from collections.abc import Sequence

import pandas as pd
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Select
from textual_plotext import PlotextPlot

from stooqie.io import get_ticker_df
from stooqie.models import TickerColumns, Tickers, settings


class StockPlotApp(App):  # type: ignore
    CSS = """
    Vertical {
        align: center middle;
        padding: 1;
    }
    Select, PlotextPlot, DataTable {margin: 1;
    }
    """

    _select_tickers: Sequence[tuple[str, str]] = [
        (ticker.display_name, ticker.ticker_name) for ticker in settings.tickers_to_track
    ]

    _default_ticker: str = Tickers.apple.ticker_name
    ticker_select = Select(_select_tickers, prompt="Select a ticker:", value=_default_ticker)

    def compose(self) -> ComposeResult:
        self.plot = PlotextPlot()
        self.data_table = DataTable()

        yield Vertical(self.ticker_select, self.plot, self.data_table)

    async def on_mount(self) -> None:
        self.data_table.add_columns("Ticker", "1 Year Diff", "2 Year Diff", "5 Year Diff")
        await self.load_ticker_data(self._default_ticker)

    @on(ticker_select.Changed)
    async def select_changed(self) -> None:
        await self.load_ticker_data(self.ticker_select.value)  # type: ignore

    async def load_ticker_data(self, ticker: str) -> None:
        df = get_ticker_df(ticker)
        df[TickerColumns.date] = pd.to_datetime(df[TickerColumns.date]).dt.strftime("%d/%m/%Y")

        plt = self.plot.plt
        plt.clf()
        plt.plot(df[TickerColumns.date], df[TickerColumns.close])  # type: ignore
        plt.title(f"Stock Prices for {ticker}")
        self.plot.refresh()

        self.data_table.clear()

        df["1Y Change"] = df[TickerColumns.close] - df["offset_one"]
        df["2Y Change"] = df[TickerColumns.close] - df["offset_five"]
        df["5Y Change"] = df[TickerColumns.close] - df["offset_ten"]

        latest_row = df.iloc[-1]
        self.data_table.add_row(
            ticker, f"{latest_row['1Y Change']:.2f}", f"{latest_row['2Y Change']:.2f}", f"{latest_row['5Y Change']:.2f}"
        )

        self.data_table.refresh()


if __name__ == "__main__":
    StockPlotApp().run()  # type: ignore

from collections.abc import Sequence

import pandas as pd
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Label, Select
from textual_plotext import PlotextPlot

from stooqie.io import get_ticker_df
from stooqie.models import TickerColumns, Tickers, settings


class StockPlotApp(App):  # type: ignore
    CSS = """
    Vertical {
        align: center top;
        height: auto;
    }
    Horizontal {
        margin-bottom: 1;
        height: auto; 
    }

    PlotextPlot {
        margin-bottom: 1;  
    }
    
    DataTable {
        margin-bottom: 1;  
    }
    
    Select {
        margin: 0;
    }
    """  # Without height: auto widgets try to occupy too much space

    BINDINGS = [Binding(key="q", action="quit", description="Quit the app")]

    _select_tickers: Sequence[tuple[str, str]] = [
        (ticker.display_name, ticker.ticker_name) for ticker in settings.tickers_to_track
    ]

    _default_ticker: str = Tickers.apple.ticker_name
    ticker_select = Select(_select_tickers, prompt="Select a ticker:", value=_default_ticker)

    _select_durations: Sequence[tuple[str, str]] = [
        ("Max", "max"),
        ("1 Year", "1"),
        ("2 Years", "2"),
        ("5 Years", "5"),
    ]
    _default_duration: str = "max"
    duration_select = Select(_select_durations, prompt="Select duration:", value=_default_duration)

    def compose(self) -> ComposeResult:
        self.plot = PlotextPlot()
        self.data_table = DataTable()

        yield Vertical(
            Horizontal(
                Vertical(Label("Select Ticker:"), self.ticker_select),
                Vertical(Label("Select Duration:"), self.duration_select),
            ),
            self.plot,
            self.data_table,
        )
        yield Footer()

    async def on_mount(self) -> None:
        self.data_table.add_columns("Ticker", "1 Year Diff", "2 Year Diff", "5 Year Diff", "Max Diff")
        await self.update_table(self._default_ticker)
        await self.update_plot(self._default_ticker, self._default_duration)

    @on(ticker_select.Changed)
    async def ticker_changed(self) -> None:
        await self.update_table(self.ticker_select.value)
        await self.update_plot(self.ticker_select.value, self.duration_select.value)

    @on(duration_select.Changed)
    async def duration_changed(self) -> None:
        await self.update_plot(self.ticker_select.value, self.duration_select.value)

    async def update_plot(self, ticker: str, duration: str) -> None:
        """Updates only the plot based on the selected duration."""
        df = get_ticker_df(ticker)
        df[TickerColumns.date] = pd.to_datetime(df[TickerColumns.date]).dt.strftime("%d/%m/%Y")

        # Apply duration filter
        if duration != "max":
            years = int(duration)
            df = df.tail(years * 252)  # Approximate trading days per year

        plt = self.plot.plt
        plt.clf()
        plt.plot(df[TickerColumns.date], df[TickerColumns.close])  # type: ignore
        plt.title(f"Stock Prices for {ticker} ({duration} years)")
        self.plot.refresh()

    async def update_table(self, ticker: str) -> None:
        """Updates only the table when the ticker is changed."""
        df = get_ticker_df(ticker)

        self.data_table.clear()

        df["1Y Change"] = df[TickerColumns.close] - df["offset_one"]
        df["2Y Change"] = df[TickerColumns.close] - df["offset_five"]
        df["5Y Change"] = df[TickerColumns.close] - df["offset_ten"]
        df["Max Change"] = df[TickerColumns.close] - df.loc[0, TickerColumns.close]

        latest_row = df.iloc[-1]
        self.data_table.add_row(
            ticker,
            f"{latest_row['1Y Change']:.2f}",
            f"{latest_row['2Y Change']:.2f}",
            f"{latest_row['5Y Change']:.2f}",
            f"{latest_row['Max Change']:.2f}",
        )

        self.data_table.refresh()


if __name__ == "__main__":
    StockPlotApp().run()  # type: ignore

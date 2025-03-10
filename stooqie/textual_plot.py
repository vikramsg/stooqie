# import pandas as pd
# from textual.app import App, ComposeResult
# from textual_plotext import PlotextPlot
#
# from stooqie.models import TickerColumns
# from stooqie.ticker import historical_change_from_ticker
#
#
# class StockPlotApp(App):  # type: ignore
#     def compose(self) -> ComposeResult:
#         yield PlotextPlot()
#
#     async def on_mount(self) -> None:
#         plt = self.query_one(PlotextPlot).plt
#
#         # Fetch historical data for a given ticker
#         ticker = "AAPL.US"
#         df = historical_change_from_ticker(ticker)
#
#         # Format the date column to the expected format
#         df_dt = pd.to_datetime(df[TickerColumns.date]).dt.strftime("%d/%m/%Y")
#
#         # Add data to the plot
#         plt.plot(df_dt, df[TickerColumns.close])
#         plt.title("Ticker plot")
#
#
# if __name__ == "__main__":
#     StockPlotApp().run()  # type: ignore
import pandas as pd
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.events import Event
from textual.widgets import DataTable, Select
from textual_plotext import PlotextPlot

from stooqie.models import TickerColumns
from stooqie.ticker import historical_change_from_ticker


class StockPlotApp(App):  # type: ignore
    CSS = """
    Vertical {
        align: center middle;
        padding: 1;
    }
    Select, PlotextPlot, DataTable {
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        self.ticker_select = Select(
            [("Apple (AAPL.US)", "AAPL.US"), ("Microsoft (MSFT.US)", "MSFT.US"), ("Amazon (AMZN.US)", "AMZN.US")],
            prompt="Select a ticker:",
        )
        self.plot = PlotextPlot()
        self.data_table = DataTable()

        yield Vertical(self.ticker_select, self.plot, self.data_table)

    async def on_mount(self) -> None:
        await self.load_ticker_data("AAPL.US")

    async def on_change(self, event: Event) -> None:
        if event.widget is self.ticker_select:
            await self.load_ticker_data(self.ticker_select.value)

    async def load_ticker_data(self, ticker: str) -> None:
        df = historical_change_from_ticker(ticker)
        df[TickerColumns.date] = pd.to_datetime(df[TickerColumns.date]).dt.strftime("%d/%m/%Y")

        plt = self.plot.plt
        plt.clf()
        plt.plot(df[TickerColumns.date], df[TickerColumns.close])
        plt.title(f"Stock Prices for {ticker}")
        self.plot.refresh()

        self.data_table.clear()
        self.data_table.add_columns("Ticker", "1 Year Diff", "2 Year Diff", "5 Year Diff")

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

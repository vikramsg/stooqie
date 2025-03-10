from textual.app import App, ComposeResult
from textual_plotext import PlotextPlot

from stooqie.models import TickerColumns
from stooqie.ticker import historical_change_from_ticker


class StockPlotApp(App):  # type: ignore
    def compose(self) -> ComposeResult:
        yield PlotextPlot()

    async def on_mount(self) -> None:
        plt = self.query_one(PlotextPlot).plt

        # Fetch historical data for a given ticker
        ticker = "AAPL.US"
        df = historical_change_from_ticker(ticker)

        # Add data to the plot
        plt.plot(df[TickerColumns.date], df[TickerColumns.close])
        plt.title("Ticker plot")


if __name__ == "__main__":
    StockPlotApp().run()  # type: ignore

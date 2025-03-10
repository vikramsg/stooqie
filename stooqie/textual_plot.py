from textual.app import App
from textual.widgets import Plot

from stooqie.ticker import historical_change_from_ticker


class StockPlotApp(App):  # type: ignore
    async def on_mount(self) -> None:
        # Create a Plot widget
        plot = Plot()

        # Fetch historical data for a given ticker
        ticker = "AAPL.US"
        df = historical_change_from_ticker(ticker)

        # Add data to the plot
        plot.add_series("Closing Prices", df["date"], df["close"])

        # Add the plot to the app
        await self.view.dock(plot, edge="top")


if __name__ == "__main__":
    StockPlotApp.run()  # type: ignore

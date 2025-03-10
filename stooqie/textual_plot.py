from textual.app import App
from textual.widgets import DataTable
from stooqie.ticker import historical_change_from_ticker

class StockPlotApp(App):
    async def on_mount(self) -> None:
        # Create a DataTable widget
        table = DataTable()
        
        # Fetch historical data for a given ticker
        ticker = "AAPL.US"
        df = historical_change_from_ticker(ticker)
        
        # Add columns to the table
        table.add_columns(*df.columns)
        
        # Add rows to the table
        for row in df.itertuples(index=False):
            table.add_row(*map(str, row))
        
        # Add the table to the app
        await self.view.dock(table, edge="top")

if __name__ == "__main__":
    StockPlotApp.run()

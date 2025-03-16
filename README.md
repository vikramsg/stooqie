# Stooqie 📈

**Stooqie** is a Python package for fetching, processing, and visualizing historical stock data from [Stooq](https://stooq.com/). It provides a CLI and a TUI dashboard for analyzing stock trends.
This project has no direct affiliation with `Stooq`.

---

## Features 🚀
- Fetch historical stock data from Stooq
- Calculate historical offsets (1, 5, 10, and 20 years)
- Visualize stock trends in a **TUI dashboard** using Textual

---

## Installation 🛠️

First clone the repo. 
After cloning, we recommend using [uv](https://docs.astral.sh/uv/).
```sh
uv sync
```

---

## Usage 📊

Download and update stock data and then open a TUI:
```sh
uv run stooqie --from-csv-file stocks.csv
```

Clean stored data:
```sh
stooqie clean
```

---

## Project Structure 🏗️
```
stooqie/
│── _ticker.py          # Fetch and process historical stock data
│── cli.py              # CLI entry point
│── dashboard.py        # TUI stock visualization
│── io.py               # Data handling and storage
│── models.py           # Data models and settings
│── utils/              # Utility functions (logging, etc.)
```

---

## License 📜
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.




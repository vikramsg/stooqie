# Stooq

Stooq is a place where stocks/ETF's are available as csv files. While its nice to have them available like that, we want to make it friendlier to do analytic queries. 

## Installation
 
Make sure you have `uv` installed, for eg using `pip insall uv && uv self update`. 

```sh
uv sync
```

## TODO

1. What we want is, given a stock, find its biggest gains, falls over a day, month, year etc. 
    - We will do this by querying a table that will have the stocks daily, monthly, yearly gains available in a parquet. 
    - If the data is not available another task will just download it and create the required parquet. 
    - The one complication we have is matching name against stock ticker. Let's hope we find some dictionary with this mapping like iso codes. 

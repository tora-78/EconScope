import requests
import pandas as pd


def get_gdp(country: str) -> pd.DataFrame:
    """Dowload GDP time series from the World Bank API."""
    url = (
    f"https://api.worldbank.org/v2/country/"
    f"{country}/indicator/NY.GDP.MKTP.CD"
    "?format=json&per_page=100"
    )
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    for record in data[1]:
        print(record["date"],record["value"])

if __name__ == "__main__":
    get_gdp("JPN")
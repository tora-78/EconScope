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
    json_data = response.json()
    years = []
    gdps = []
    for record in json_data[1]:
        years.append(int(record["date"]))
        gdps.append(record["value"])
        if record["value"] is None:
            continue
    df = pd.DataFrame({
        "year": years,
        "GDP": gdps
    })
    return df

if __name__ == "__main__":
    df = get_gdp("JPN")
    print(df)
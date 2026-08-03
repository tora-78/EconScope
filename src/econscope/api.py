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
        if record["value"] is None:
            continue
        years.append(int(record["date"]))
        gdps.append(record["value"])

    df = pd.DataFrame({
        "year": years,
        "GDP": gdps
    })
    return df

if __name__ == "__main__":
    df = get_gdp("JPN")
    print(df)

def get_country_list() -> pd.DataFrame:
    """Download the country list from the World Bank API."""
    url = "https://api.worldbank.org/v2/country?format=json&per_page=400"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    json_data = response.json()

    codes = []
    names = []
    regions = []
    income_levels = []

    for record in json_data[1]:
        if record["incomeLevel"]["value"] == "Aggregates":
            continue
        codes.append(record["id"])
        names.append(record["name"])
        regions.append(record["region"]["value"].strip())
        income_levels.append(record["incomeLevel"]["value"])

    df = pd.DataFrame({
    "country_code": codes,
    "country_name": names,
    "region": regions,
    "income_level": income_levels,
    })
    return df

if __name__ == "__main__":
    df = get_country_list()
    print(df)
    print(df["region"].unique())
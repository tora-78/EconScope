import pandas as pd
import requests
import time


class WorldBankAPIError(RuntimeError):
    """Raised when data cannot be retrieved from the World Bank API."""


def _get_json(url: str) -> list:
    """Fetch JSON from the World Bank API, retrying temporary server failures."""
    last_error: Exception | None = None

    for attempt in range(3):
        try:
            response = requests.get(url, timeout=20)
            # The World Bank API intermittently returns 502 for individual
            # countries. Retrying can succeed without changing the country code.
            if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2**attempt)
                continue
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as error:
            last_error = error

    raise WorldBankAPIError(
        "The World Bank API is temporarily unavailable for this request. "
        "Please try again later."
    ) from last_error


def get_gdp(country: str) -> pd.DataFrame:
    """Download GDP time series from the World Bank API."""
    url = (
    f"https://api.worldbank.org/v2/country/"
    f"{country}/indicator/NY.GDP.MKTP.CD"
    "?format=json&per_page=100"
    )
    json_data = _get_json(url)
    if len(json_data) < 2 or not isinstance(json_data[1], list):
        raise WorldBankAPIError(f"No GDP data is available for country code {country}.")
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
    json_data = _get_json(url)

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

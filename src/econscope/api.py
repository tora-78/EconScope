import pandas as pd
import requests
import time


class DataSourceError(RuntimeError):
    """Raised when an economic-data source cannot be reached or parsed."""


class WorldBankAPIError(DataSourceError):
    """Raised when data cannot be retrieved from the World Bank API."""


def _get_json(
    url: str,
    source_name: str,
    error_type: type[DataSourceError] = DataSourceError,
) -> object:
    """Fetch JSON from a data source, retrying temporary server failures."""
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

    raise error_type(
        f"{source_name} is temporarily unavailable for this request. "
        "Please try again later."
    ) from last_error


def _gdp_dataframe(years: list[object], values: list[object]) -> pd.DataFrame:
    """Convert aligned year and GDP-value lists to the app's common format."""
    df = pd.DataFrame(
        zip(years, values, strict=True), columns=["year", "GDP"]
    )
    # DBnomics may encode missing observations as strings such as "NA".
    # Matplotlib requires one numeric dtype rather than a mix of strings/floats.
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["GDP"] = pd.to_numeric(df["GDP"], errors="coerce")
    return df.dropna(subset=["year", "GDP"]).astype({"year": int}).sort_values("year")


def get_gdp_from_world_bank(country: str) -> pd.DataFrame:
    """Download GDP time series from the World Bank API."""
    url = (
    f"https://api.worldbank.org/v2/country/"
    f"{country}/indicator/NY.GDP.MKTP.CD"
    "?format=json&per_page=100"
    )
    json_data = _get_json(url, "The World Bank API", WorldBankAPIError)
    if len(json_data) < 2 or not isinstance(json_data[1], list):
        raise WorldBankAPIError(f"No GDP data is available for country code {country}.")
    years = [record["date"] for record in json_data[1]]
    gdps = [record["value"] for record in json_data[1]]
    return _gdp_dataframe(years, gdps)


def get_gdp_from_dbnomics(country: str) -> pd.DataFrame:
    """Download the same WDI GDP series through DBnomics as a fallback."""
    url = (
        "https://api.db.nomics.world/v22/series/WB/WDI/"
        f"A-NY.GDP.MKTP.CD-{country}?observations=1"
    )
    json_data = _get_json(url, "The DBnomics API")

    try:
        series = json_data["series"]["docs"][0]
        years = series["period"]
        gdps = series["value"]
    except (KeyError, IndexError, TypeError) as error:
        raise DataSourceError(
            f"No fallback GDP data is available for country code {country}."
        ) from error

    return _gdp_dataframe(years, gdps)


def get_gdp(country: str) -> pd.DataFrame:
    """Download GDP, falling back to DBnomics if the World Bank API fails."""
    try:
        return get_gdp_from_world_bank(country)
    except WorldBankAPIError as world_bank_error:
        try:
            return get_gdp_from_dbnomics(country)
        except DataSourceError as dbnomics_error:
            raise DataSourceError(
                "GDP data could not be retrieved from the World Bank or DBnomics."
            ) from dbnomics_error


if __name__ == "__main__":
    df = get_gdp("JPN")
    print(df)

def get_country_list() -> pd.DataFrame:
    """Download the country list from the World Bank API."""
    url = "https://api.worldbank.org/v2/country?format=json&per_page=400"
    json_data = _get_json(url, "The World Bank API", WorldBankAPIError)

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

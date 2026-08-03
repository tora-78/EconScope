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


def _indicator_dataframe(
    years: list[object], values: list[object], value_column: str
) -> pd.DataFrame:
    """Convert aligned indicator observations to the app's common format."""
    df = pd.DataFrame(
        zip(years, values, strict=True), columns=["year", value_column]
    )
    # DBnomics may encode missing observations as strings such as "NA".
    # Matplotlib requires one numeric dtype rather than a mix of strings/floats.
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df[value_column] = pd.to_numeric(df[value_column], errors="coerce")
    return (
        df.dropna(subset=["year", value_column])
        .astype({"year": int})
        .sort_values("year")
    )


def _get_indicator_from_world_bank(
    country: str, indicator_code: str, value_column: str
) -> pd.DataFrame:
    """Download a World Bank indicator time series."""
    url = (
        f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}"
        "?format=json&per_page=100"
    )
    json_data = _get_json(url, "The World Bank API", WorldBankAPIError)
    if len(json_data) < 2 or not isinstance(json_data[1], list):
        raise WorldBankAPIError(
            f"No {value_column} data is available for country code {country}."
        )
    years = [record["date"] for record in json_data[1]]
    values = [record["value"] for record in json_data[1]]
    return _indicator_dataframe(years, values, value_column)


def _get_indicator_from_dbnomics(
    country: str, indicator_code: str, value_column: str
) -> pd.DataFrame:
    """Download a WDI indicator through DBnomics as a fallback."""
    url = (
        "https://api.db.nomics.world/v22/series/WB/WDI/"
        f"A-{indicator_code}-{country}?observations=1"
    )
    json_data = _get_json(url, "The DBnomics API")

    try:
        series = json_data["series"]["docs"][0]
        years = series["period"]
        gdps = series["value"]
    except (KeyError, IndexError, TypeError) as error:
        raise DataSourceError(
            f"No fallback {value_column} data is available for country code {country}."
        ) from error

    return _indicator_dataframe(years, gdps, value_column)


def _get_indicator(country: str, indicator_code: str, value_column: str) -> pd.DataFrame:
    """Download an indicator, falling back to DBnomics if World Bank fails."""
    try:
        return _get_indicator_from_world_bank(country, indicator_code, value_column)
    except WorldBankAPIError:
        try:
            return _get_indicator_from_dbnomics(country, indicator_code, value_column)
        except DataSourceError as error:
            raise DataSourceError(
                f"{value_column} data could not be retrieved from the World Bank or DBnomics."
            ) from error


def get_gdp(country: str) -> pd.DataFrame:
    """Download GDP (current US$) time series."""
    return _get_indicator(country, "NY.GDP.MKTP.CD", "GDP")


def get_population(country: str) -> pd.DataFrame:
    """Download total population time series."""
    return _get_indicator(country, "SP.POP.TOTL", "Population")


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

import matplotlib.pyplot as plt
from api import get_gdp, get_population


def _plot_indicator(country: str, column: str, title: str, y_label: str, df) -> None:
    """Draw an indicator time series using the common dataframe format."""
    if df.empty:
        raise ValueError(f"No {column.lower()} observations are available for {country}.")

    plt.figure(figsize=(10, 5))
    plt.plot(df["year"], df[column])

    plt.title(f"{country} {title}")
    plt.xlabel("Year")
    plt.ylabel(y_label)

    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_gdp(country: str) -> None:
    """Draw a GDP (current US$) chart."""
    _plot_indicator(country, "GDP", "GDP", "GDP (current US$)", get_gdp(country))


def plot_population(country: str) -> None:
    """Draw a total-population chart."""
    _plot_indicator(
        country,
        "Population",
        "Population",
        "Population (people)",
        get_population(country),
    )

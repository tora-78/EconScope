import matplotlib.pyplot as plt

try:
    from .indicators import GDP, POPULATION, Indicator, get_indicator
except ImportError:  # Supports running source files directly during development.
    from indicators import GDP, POPULATION, Indicator, get_indicator


def plot_indicator(country: str, indicator: Indicator) -> None:
    """Retrieve and draw a time series for the selected indicator."""
    df = get_indicator(country, indicator)
    if df.empty:
        raise ValueError(f"No {indicator.name.lower()} observations are available for {country}.")

    plt.figure(figsize=(10, 5))
    plt.plot(df["year"], df[indicator.column])

    plt.title(f"{country} {indicator.name}")
    plt.xlabel("Year")
    plt.ylabel(indicator.y_label)

    plt.grid(True)
    plt.tight_layout()
    plt.savefig("gdp.png")
    plt.show()


def plot_gdp(country: str) -> None:
    """Draw a GDP (current US$) chart."""
    plot_indicator(country, GDP)


def plot_population(country: str) -> None:
    """Draw a total-population chart."""
    plot_indicator(country, POPULATION)

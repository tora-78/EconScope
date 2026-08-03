"""Definitions and access functions for EconScope's supported indicators."""

from dataclasses import dataclass

import pandas as pd

try:
    from .api import get_indicator_data
except ImportError:  # Supports running source files directly during development.
    from api import get_indicator_data


@dataclass(frozen=True)
class Indicator:
    """Metadata needed to retrieve and display one economic indicator."""

    name: str
    code: str
    column: str
    y_label: str


GDP = Indicator(
    name="GDP",
    code="NY.GDP.MKTP.CD",
    column="GDP",
    y_label="GDP (current US$)",
)
POPULATION = Indicator(
    name="Population",
    code="SP.POP.TOTL",
    column="Population",
    y_label="Population (people)",
)

INDICATORS = {
    "1": GDP,
    "2": POPULATION,
}


def get_indicator(country: str, indicator: Indicator) -> pd.DataFrame:
    """Retrieve a supported indicator in the common year/value dataframe format."""
    return get_indicator_data(country, indicator.code, indicator.column)


def get_gdp(country: str) -> pd.DataFrame:
    """Retrieve GDP (current US$)."""
    return get_indicator(country, GDP)


def get_population(country: str) -> pd.DataFrame:
    """Retrieve total population."""
    return get_indicator(country, POPULATION)

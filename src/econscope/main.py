import pandas as pd
from api import get_country_list
from visualize import plot_gdp

VERSION = "0.1.0"

def print_welcome() -> None:
    print("=" * 60)
    print("                    Welcome to EconScope")
    print(f"                    Version {VERSION}")
    print("=" * 60)
    print()
    print("EconScope is an economic data explorer powered")
    print("by the World Bank Open Data API.")
    print()
    print("Available indicators include:")
    print("  • GDP")
    print("  • Population")
    print("  • Life Expectancy")
    print("  • CO₂ Emissions")
    print()


REGIONS = {
    1: "East Asia & Pacific",
    2: "Europe & Central Asia",
    3: "Latin America & Caribbean",
    4: "Middle East, North Africa, Afghanistan & Pakistan",
    5: "North America",
    6: "South Asia",
    7: "Sub-Saharan Africa",
}

def select_region() -> str | None:
    """Ask the user to select a World Bank region."""

    print("""
    Select a World Bank Region

    1. East Asia & Pacific
    2. Europe & Central Asia
    3. Latin America & Caribbean
    4. Middle East, North Africa, Afghanistan & Pakistan
    5. North America
    6. South Asia
    7. Sub-Saharan Africa
    0. Exit
    """)

    choice = int(input("Enter your choice: "))
    if choice == 0:
        return None

    return REGIONS[choice]

def select_country(countries: pd.DataFrame, region: str) -> str:
    """Ask the user to select a country from a region."""

    region_df = countries[countries["region"] == region]
    print(f"\nCountries in {region}:\n")
    for _, row in region_df.iterrows():
        print(f'{row["country_code"]:<5} {row["country_name"]}')
    country = input("\nEnter country code: ").upper()

    return country

def main():
    print_welcome()
    region = select_region()
    if region is None:
        return
    countries = get_country_list()
    country = select_country(countries, region)
    plot_gdp(country)

if __name__ == "__main__":
    main()
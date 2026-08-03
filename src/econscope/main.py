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

    while True:
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

        choice = input("Enter your choice: ")
        if choice == 0:
            return None
        if choice.isdigit() and int(choice) in REGIONS:
            return REGIONS[int(choice)]
        print("\nInvalid region number. Please try again.\n")


def select_country(countries: pd.DataFrame, region: str) -> str:
    """Ask the user to select a country from a region."""

    region_df = countries[countries["region"] == region]
    print(f"\nCountries in {region}:\n")
    for _, row in region_df.iterrows():
        print(f'{row["country_code"]:<5} {row["country_name"]}')
    valid_codes = set(region_df["country_code"])
    while True:
        country = input("\nEnter country code: ").upper()
        if country in valid_codes:
            return country
        print("\nInvalid country code. Please try again.\n")

def main():
    print_welcome()

    while True:
        region = select_region()
        if region is None:
            print("\nThank you for using EconScope. Goodbye!")
            break
        countries = get_country_list()
        country = select_country(countries, region)
        print("\nDownloading data and generating the GDP chart...")
        plot_gdp(country)
        print("\n✓ GDP trend chart generated successfully!")
        print("""
        What would you like to do next?

        1. View another country
        0. Exit
        """)

        choice = input("Enter your choice: ")
        if choice == "0":
            print("\nThank you for using EconScope. Goodbye!")
            break

if __name__ == "__main__":
    main()
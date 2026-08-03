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

    print("Select a region:")
    print()

    print("1. Africa")
    print("2. Asia")
    print("3. Europe")
    print("4. North America")
    print("5. South America")
    print("6. Oceania")
    print("7. Show all countries")
    print("0. Exit")

    choice = input("\nEnter your choice: ")

    print(choice)

def main():
    print_welcome()

if __name__ == "__main__":
    main()
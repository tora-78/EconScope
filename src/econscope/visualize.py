def plot_gdp(country: str) -> None:
    df = get_gdp(country)

    plt.figure(figsize=(10, 5))
    plt.plot(df["year"], df["GDP"])

    plt.title(f"{country} GDP")
    plt.xlabel("Year")
    plt.ylabel("GDP (current US$)")

    plt.grid(True)
    plt.tight_layout()
    plt.show()
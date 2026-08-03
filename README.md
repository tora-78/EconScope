# EconScope

EconScope is a command-line application for exploring country-level economic data. Select an indicator, choose a World Bank region and country, and view its historical trend as a chart.

## Features

- Interactive GDP and total-population charts.
- Country selection across seven World Bank regions.
- GDP measured in current US dollars; population measured as total people.
- World Bank Open Data API as the primary source.
- Automatic DBnomics fallback when the World Bank indicator endpoint is temporarily unavailable.
- Input validation and user-friendly errors instead of raw API tracebacks.
- Automated test suite run by GitHub Actions.

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
git clone https://github.com/tora-78/EconScope.git
cd EconScope
uv sync
```

`uv sync` creates the environment and installs both the application and development dependencies.

## Usage

Run the application with:

```bash
uv run src/econscope/main.py
```

The program first asks which indicator to display, then guides you through region and country selection:

```text
Select an indicator

1. GDP
2. Population
0. Exit
```

For example, choose `2` for Europe & Central Asia and enter `TJK` to view Tajikistan's selected indicator. Close the chart window to return to the menu.

## Supported indicators

| Indicator | World Bank code | Unit |
| --- | --- | --- |
| GDP | `NY.GDP.MKTP.CD` | Current US$ |
| Population | `SP.POP.TOTL` | People |

## Data sources and reliability

EconScope requests World Bank World Development Indicators data first. If that API returns a temporary service error, such as HTTP 502, the application retries the request and then falls back to the corresponding World Development Indicators series served through DBnomics.

This keeps the indicator definition consistent while avoiding failures caused by temporary problems at one API endpoint. Both sources still depend on their underlying data coverage and update schedules.

## Running tests

```bash
uv run pytest -q
```

The tests run without contacting external APIs: HTTP calls are mocked to cover data parsing, fallback behavior, indicator configuration, menu validation, and chart metadata.

## Project structure

```text
src/econscope/
├── api.py          # HTTP requests, retries, and source fallback
├── indicators.py   # Indicator metadata and GDP/population access functions
├── visualize.py    # Matplotlib chart rendering
├── main.py         # Command-line menu and application flow
└── __init__.py     # Package entry point

tests/
└── test_api.py     # Offline unit tests

.github/workflows/
└── main.yml        # GitHub Actions test workflow
```

## References

- [World Bank Indicators API documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation)
- [DBnomics documentation](https://docs.db.nomics.world/)

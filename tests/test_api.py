"""Offline tests for EconScope data retrieval, indicators, and charting."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("MPLCONFIGDIR", "/tmp/econscope-matplotlib")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "econscope"))

from econscope import api, indicators, main, visualize


class IndicatorDataTests(unittest.TestCase):
    def test_indicator_dataframe_removes_missing_non_numeric_values(self) -> None:
        df = api._indicator_dataframe(
            ["2021", "2022", "2023"], ["NA", 9_950_000, "10200000"], "Population"
        )

        self.assertEqual(
            df.to_dict("records"),
            [
                {"year": 2022, "Population": 9_950_000},
                {"year": 2023, "Population": 10_200_000},
            ],
        )

    @patch.object(api, "_get_json")
    def test_get_population_parses_world_bank_response(self, mock_get_json) -> None:
        mock_get_json.return_value = [
            {},
            [
                {"date": "2024", "value": 10_200_000},
                {"date": "2023", "value": None},
                {"date": "2022", "value": 9_950_000},
            ],
        ]

        df = indicators.get_population("TJK")

        self.assertEqual(list(df.columns), ["year", "Population"])
        self.assertEqual(df["year"].tolist(), [2022, 2024])
        self.assertEqual(df["Population"].tolist(), [9_950_000, 10_200_000])
        self.assertIn("SP.POP.TOTL", mock_get_json.call_args.args[0])

    @patch.object(api, "_get_indicator_from_dbnomics")
    @patch.object(api, "_get_indicator_from_world_bank")
    def test_falls_back_to_dbnomics_when_world_bank_fails(
        self, mock_world_bank, mock_dbnomics
    ) -> None:
        mock_world_bank.side_effect = api.WorldBankAPIError("502")
        fallback_data = api._indicator_dataframe(["2024"], [10_200_000], "Population")
        mock_dbnomics.return_value = fallback_data

        df = api.get_indicator_data("TJK", "SP.POP.TOTL", "Population")

        self.assertTrue(df.equals(fallback_data))
        mock_dbnomics.assert_called_once_with("TJK", "SP.POP.TOTL", "Population")

    @patch.object(api, "_get_json")
    def test_country_list_excludes_aggregates(self, mock_get_json) -> None:
        mock_get_json.return_value = [
            {},
            [
                {
                    "id": "TJK",
                    "name": "Tajikistan",
                    "region": {"value": "Europe & Central Asia"},
                    "incomeLevel": {"value": "Lower middle income"},
                },
                {
                    "id": "WLD",
                    "name": "World",
                    "region": {"value": "Aggregates"},
                    "incomeLevel": {"value": "Aggregates"},
                },
            ],
        ]

        countries = api.get_country_list()

        self.assertEqual(countries.to_dict("records")[0]["country_code"], "TJK")
        self.assertEqual(len(countries), 1)


class IndicatorConfigurationTests(unittest.TestCase):
    def test_indicator_metadata_matches_expected_world_bank_codes(self) -> None:
        self.assertEqual(indicators.GDP.code, "NY.GDP.MKTP.CD")
        self.assertEqual(indicators.POPULATION.code, "SP.POP.TOTL")
        self.assertEqual(indicators.INDICATORS["2"], indicators.POPULATION)

    @patch("indicators.get_indicator_data")
    def test_get_gdp_uses_gdp_metadata(self, mock_get_indicator_data) -> None:
        mock_get_indicator_data.return_value = api._indicator_dataframe(
            ["2024"], [1.0], "GDP"
        )

        indicators.get_gdp("JPN")

        mock_get_indicator_data.assert_called_once_with("JPN", "NY.GDP.MKTP.CD", "GDP")


class UserInterfaceTests(unittest.TestCase):
    @patch("builtins.input", side_effect=["9", "2"])
    def test_indicator_selection_retries_after_invalid_input(self, mock_input) -> None:
        selected = main.select_indicator()

        self.assertEqual(selected, indicators.POPULATION)
        self.assertEqual(mock_input.call_count, 2)

    @patch("visualize.plt.show")
    @patch("visualize.get_indicator")
    def test_population_chart_uses_population_column(self, mock_get_indicator, mock_show) -> None:
        mock_get_indicator.return_value = api._indicator_dataframe(
            ["2023", "2024"], [9_950_000, 10_200_000], "Population"
        )

        visualize.plot_indicator("TJK", indicators.POPULATION)

        axis = visualize.plt.gca()
        self.assertEqual(axis.get_ylabel(), "Population (people)")
        self.assertEqual(axis.get_title(), "TJK Population")
        mock_show.assert_called_once()
        visualize.plt.close("all")


if __name__ == "__main__":
    unittest.main()

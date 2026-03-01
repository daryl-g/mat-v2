# API data scrapers

# Imports
import os
import json
import requests
import streamlit as st

from loguru import logger
from time import sleep
from dotenv import load_dotenv

# Load global env variables
load_dotenv()


@st.cache_resource
class Scrapers:
    """
    Scraper functions from different data sources via API calls.
    """

    _REQUEST_TIMEOUT = 30

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
            }
        )

    def opta_scraper(self, match_id: str) -> dict | None:
        """
        Scrape match data from Opta API.

        Args:
            match_id (str): The unique match identifier to scrape.

        Returns:
            dict: A dictionary containing the scraped match data. Returns None if scraping fails.
        """

        # Load the key from environment variables
        opta_api_key: str | None = os.getenv("OPTA_KEY")
        if not opta_api_key:
            logger.error("OPTA_KEY not found in environment variables.")
            return

        # Add referer for Opta API requests
        self._session.headers.update({"Referer": "https://dataviz.theanalyst.com/"})

        # Additional params
        ## _rt=c: Request type/operating mode (c or b)
        ## _lcl=en: Language for Opta assets (en for English)
        ## _fmt=json: Response format (json or xml)
        additional_params = "_rt=c&_lcl=en&_fmt=json"

        opta_endpoints = {
            "matchstats": "stats",
            "matchevent": "events",
            "matchexpectedgoals": "xgoal",
            "passmatrix": "passmap",
        }

        # Construct the URLs
        opta_urls = [
            f"https://api.performfeeds.com/soccerdata/{endpoint}/{opta_api_key}/{match_id}?{additional_params}"
            for endpoint in opta_endpoints.keys()
        ]

        # Scrape the match stats first
        match_stats_response = self._session.get(
            opta_urls[0], timeout=self._REQUEST_TIMEOUT
        )
        if match_stats_response.status_code != 200:
            st.error(f"Failed to fetch match stats: {match_stats_response.status_code}")
            return

        coverage_tier_info = self._opta_coverage_tier_check(
            stats_data=match_stats_response.json()
        )
        if not coverage_tier_info:
            return

        coverage_tier = coverage_tier_info["coverage_level"]

        # Coverage tier must include event data to proceed
        if coverage_tier not in [10, 12, 13, 14, 15]:
            st.error(
                f"Coverage tier does not contain event data: {coverage_tier}. Cannot proceed with scraping."
            )
            return

        logger.info(
            f"Coverage tier contains event data: {coverage_tier}. Scraping starts..."
        )

        home_team_short = coverage_tier_info["home_team_short"]
        away_team_short = coverage_tier_info["away_team_short"]
        prefix = f"data/tmp/{home_team_short}_{away_team_short}"

        with st.spinner("Scraping Opta data..."):
            for i, (endpoint, suffix) in enumerate(list(opta_endpoints.items())[1:]):
                url = opta_urls[i + 1]
                response = self._session.get(url, timeout=self._REQUEST_TIMEOUT)
                if response.status_code != 200:
                    st.markdown(
                        f"- ❌ Failed to fetch {endpoint} (Status code: {response.status_code})"
                    )
                else:
                    with open(
                        f"{prefix}_{suffix}.json", mode="w", encoding="utf-8"
                    ) as f:
                        json.dump(response.json(), f)

                # Sleep between requests to avoid rate limits, but not after the last one
                if i < len(opta_endpoints) - 2:
                    sleep(60)

        # Report saved files
        for saved_file in os.listdir("data/tmp"):
            if any(
                saved_file.endswith(s)
                for s in ("stats.json", "events.json", "xgoal.json", "passmap.json")
            ):
                st.markdown(f"- ✅ {saved_file} saved successfully!")
            elif saved_file.endswith("temp.json"):
                continue  # Ignore temp.json file
            else:
                st.markdown(f"- ❌ {saved_file} - Unrecognised file!")

        return {
            "stats": f"{prefix}_stats.json",
            "events": f"{prefix}_events.json",
            "xgoals": f"{prefix}_xgoal.json",
            "passmap": f"{prefix}_passmap.json",
        }

    def _opta_coverage_tier_check(self, stats_data: dict) -> dict | None:
        """
        Check the coverage tier of the Opta match data and save the stats file.

        Args:
            stats_data (dict): The JSON data from the Opta match stats API response.

        Returns:
            dict | None: A dict with ``coverage_level``, ``home_team_short``, and
            ``away_team_short`` if the coverage level is valid; ``None`` otherwise.
        """
        if not stats_data:
            st.error("No stats data provided for coverage tier check.")
            return

        match_info = stats_data.get("matchInfo", {})

        # Extract and validate the coverage level
        coverage_level = match_info.get("coverageLevel")
        if coverage_level is None:
            st.error("Coverage level not found in match stats data.")
            return

        coverage_level = int(coverage_level)
        if coverage_level not in [10, 12, 13, 14, 15]:
            st.error(
                f"Opta coverage level does not contain event data. Coverage level: {coverage_level}"
            )
            return

        st.success(
            f"Opta coverage level contains event data. Coverage level: {coverage_level}"
        )

        # Resolve team codes by position rather than by index
        contestants = match_info.get("contestant", [])
        home_team_short = next(
            (c.get("code", "HOME") for c in contestants if c.get("position") == "home"),
            "HOME",
        )
        away_team_short = next(
            (c.get("code", "AWAY") for c in contestants if c.get("position") == "away"),
            "AWAY",
        )

        # Save the stats file to tmp for later use
        with open(
            f"data/tmp/{home_team_short}_{away_team_short}_stats.json",
            mode="w",
            encoding="utf-8",
        ) as f:
            json.dump(stats_data, f)

        return {
            "coverage_level": coverage_level,
            "home_team_short": home_team_short,
            "away_team_short": away_team_short,
        }

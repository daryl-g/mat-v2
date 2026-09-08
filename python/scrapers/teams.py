# Scrape all teams in a competition and update the JSON file

# Imports
import uuid
import json
import os.path
import requests
import pandas as pd

from io import StringIO
from loguru import logger
from bs4 import BeautifulSoup
from dotenv import dotenv_values

# ----------------------------------------------------------


def teams_scraper(tournament: str = "", tournament_year: str = "") -> bool:
    """
    Scraper to scrape Wikipedia for team information of a specific competition and update the JSON file.

    Args:
        tournament (str): Tournament name, as listed on Wikipedia.
        tournament_year (str): Year of the tournament as a string.

    Returns:
        bool: True if the scraping process was successful, False if it was not.
    """
    try:
        int(tournament_year)
    except ValueError:
        raise ValueError(
            f"Entered tournament year ({tournament_year}) is not a valid number!"
        )

    logger.info(f"Scraping teams for the {tournament_year} {tournament}")

    request = requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/html/{tournament_year}_{tournament.replace(" ", "_")}",
        headers={
            "User-Agent": f"Match-Analysis-App/1.0 ({dotenv_values('../.env')['EMAIL']})"
        },
    )

    teams_soup = BeautifulSoup(request.text, "html.parser")
    all_tables = pd.read_html(
        StringIO(str(teams_soup.find_all("table", {"class": "wikitable"})))
    )[:2]

    teams_list = []
    teams_raw = [table.columns for table in all_tables if "Team" in table.columns]

    for team in teams_raw.values:
        teams_list.append(
            {
                "id": (uuid.uuid4().hex)[:16],
                "fullName": team,
                "shortName": team,
                "code": "",
                "primaryColor": "",
                "textColor": "",
                "flag": "",
            }
        )

    logger.info(
        f"All teams from the {tournament_year} {tournament}: {teams_raw.to_list()}"
    )

    # Write standings to JSON file
    with open("teams.json", "w", encoding="utf-8") as f:
        json.dump({"teams": teams_list}, f, indent=3, ensure_ascii=False)
        f.close()

    # Validate scrape and file write
    if os.path.isfile("teams.json"):
        logger.success(
            f"Successfully scraped all teams from the {tournament_year} {tournament}!"
        )
        return True
    else:
        logger.error(
            f"Failed to scrape all teams from the {tournament_year} {tournament}!"
        )
        return False

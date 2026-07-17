# Scrape results and standings from Wikipedia and update the JSON files

# Imports
import os
import json
import requests
import pandas as pd

from time import sleep
from io import StringIO
from loguru import logger
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------
folder_path = "data/opta/2026 ASEAN Championship/"

# Load lookup tables
with open(folder_path + "groups.json", "r") as f:
    groups_data = json.load(f)
    f.close()

groups_lookup = pd.DataFrame(groups_data["groups"])
logger.success("Loaded groups lookup table")

with open(folder_path + "teams.json", "r") as f:
    teams_data = json.load(f)
    f.close()

teams_lookup = pd.DataFrame(teams_data["teams"])
logger.success("Loaded teams lookup table")

# ----------------------------------------------------------

# Scrape group standings from Wikipedia
standings = []

for group in groups_lookup["name"]:
    request = requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/html/2026_ASEAN_Championship_{group.replace(' ', '_')}",
        headers={"User-Agent": f"Match-Analysis-App/1.0 ({os.environ['EMAIL']})"},
    )

    soup = BeautifulSoup(request.text, "html.parser")
    table = pd.read_html(StringIO(str(soup.find_all("table", {"class": "wikitable"}))))[
        1
    ]

    # Remove host tag from team name
    table["Teamvte"] = table["Teamvte"].str.replace(r"\s*\(H\)", "", regex=True)

    # Add teamId and short team name
    team_ids = []
    short_names = []
    flags = []
    for team in table["Teamvte"]:
        team_info = teams_lookup[
            (teams_lookup["fullName"] == team) | (teams_lookup["shortName"] == team)
        ].reset_index(drop=True)
        # General cases
        if not team_info.empty:
            team_ids.append(team_info.loc[0, "id"] if len(team_info) > 0 else None)
            short_names.append(
                team_info.loc[0, "shortName"] if len(team_info) > 0 else None
            )
            flags.append(team_info.loc[0, "flag"] if len(team_info) > 0 else None)
        # Special cases
        # else:
        #     # Wikipedia name - FIFA-recognised name
        #     special_cases = {}
        #     team_info = teams_lookup[
        #         teams_lookup["fullName"] == special_cases.get(team, team)
        #     ].reset_index(drop=True)
        #     team_ids.append(team_info.loc[0, "id"] if len(team_info) > 0 else None)
        #     short_names.append(
        #         team_info.loc[0, "shortName"] if len(team_info) > 0 else None
        #     )
        #     flags.append(team_info.loc[0, "flag"] if len(team_info) > 0 else None)

    # Add teamId column to table
    table["id"] = pd.Series(team_ids)
    table["shortName"] = pd.Series(short_names)
    table["flag"] = pd.Series(flags)

    # Some pre-processing steps
    ## Rename columns
    table.rename(
        columns={
            "Teamvte": "teamName",
            "Pos": "position",
            "Pld": "played",
            "W": "wins",
            "D": "draws",
            "L": "losses",
            "GF": "goalsScored",
            "GA": "goalsConceded",
            "GD": "goalDiff",
            "Pts": "points",
        },
        inplace=True,
    )

    ## Drop unnecessary columns
    table.drop(columns=["Qualification"], inplace=True, errors="ignore")

    ## Move id column in front of teamName
    cols = table.columns.tolist()
    cols.insert(0, cols.pop(cols.index("id")))
    table = table[cols]

    # Convert to dict and add to standings
    standings.append(
        {
            "id": groups_lookup[groups_lookup["name"] == group]["id"].iloc[0],
            "name": group,
            "teams": table.to_dict(orient="records"),
        }
    )

    logger.success(f"Scraped standings for {group}")
    sleep(1)

# ----------------------------------------------------------

# Write standings to JSON file
with open(folder_path + "standings.json", "w", encoding="utf-8") as f:
    json.dump({"standings": standings}, f, indent=3, ensure_ascii=False)
    f.close()

logger.success("Saved standings to standings.json")

# Scrape team squads from Wikipedia and update the JSON files

# Imports
import os
import uuid
import json
import requests
import pandas as pd

from time import sleep
from io import StringIO
from loguru import logger
from bs4 import BeautifulSoup
from dotenv import dotenv_values

# ----------------------------------------------------------
# Load lookup data

folder_path = "data/opta/2026 ASEAN Championship/"

with open(folder_path + "teams.json", "r") as f:
    teams_data = json.load(f)
    f.close()

teams_lookup = pd.DataFrame(teams_data["teams"])
logger.success("Loaded teams lookup table")

# ----------------------------------------------------------

squads = []

# Scrape squads data from Wikipedia
squad_request = requests.get(
    "https://en.wikipedia.org/api/rest_v1/page/html/2026_ASEAN_Championship_squads",
    headers={
        "User-Agent": f"Match-Analysis-App/1.0 ({dotenv_values('../../.env')['EMAIL']})"
    },
)

squad_soup = BeautifulSoup(squad_request.text, "html.parser")

# Extract data from the HTML
all_teams = squad_soup.find_all("h3")[:10]
all_squads = squad_soup.find_all("table", {"class": "wikitable"})

for i in range(len(all_teams)):
    team_name = all_teams[i].text.strip()

    # Find team ID
    if (team_name in teams_lookup["fullName"].values) | (
        team_name in teams_lookup["shortName"].values
    ):
        team_id = teams_lookup[
            (teams_lookup["fullName"] == team_name)
            | (teams_lookup["shortName"] == team_name)
        ]["id"].iloc[0]
    else:
        # Handle special cases where Wikipedia name differs from FIFA-recognised name
        special_cases = {}
        team_id = teams_lookup[
            teams_lookup["fullName"] == special_cases.get(team_name, team_name)
        ]["id"].iloc[0]

    # Extract squad table
    squad_table = pd.read_html(StringIO(str(all_squads[i])))[0]

    if (len(squad_table) != 0) and ("Player" in squad_table.columns):
        # Retain relevant columns
        squad_table = squad_table[["No.", "Player", "Pos.", "Club"]]

        squad_table.rename(
            columns={
                "No.": "shirtNumber",
                "Player": "playerName",
                "Pos.": "position",
                "Club": "parentClub",
            },
            inplace=True,
        )

        # Drop rows with NaN values in playerName column
        squad_table.dropna(subset=["playerName"], inplace=True)

        # Fill in missing shirt numbers with 0
        squad_table["shirtNumber"] = squad_table["shirtNumber"].fillna(0)

        # Add player IDs
        player_ids = []
        for player in squad_table["playerName"]:
            player_ids.append((uuid.uuid4().hex)[:16])

            # Remove captain tag if found
            if player.endswith(" (captain)"):
                squad_table.loc[squad_table["playerName"] == player, "playerName"] = (
                    player.replace(" (captain)", "")
                )
        squad_table["id"] = pd.Series(player_ids)

        # Move id column to the front
        cols = squad_table.columns.tolist()
        cols.insert(0, cols.pop(cols.index("id")))
        squad_table = squad_table[cols]

        # Fill in missing player IDs with new UUIDs
        squad_table["id"] = squad_table["id"].apply(
            lambda x: (uuid.uuid4().hex)[:16] if pd.isna(x) else x
        )

        # Add team squad to squads list
        squads.append(
            {
                "teamId": team_id,
                "teamName": team_name,
                "players": squad_table.to_dict(orient="records"),
            }
        )

# ----------------------------------------------------------
# Write squads to JSON file
with open(folder_path + "squads.json", "w", encoding="utf-8") as f:
    json.dump({"squads": squads}, f, indent=3, ensure_ascii=False)
    f.close()

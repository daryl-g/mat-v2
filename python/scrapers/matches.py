# Scrape results and standings from Wikipedia and update the JSON files

# Imports
import os
import re
import uuid
import json
import requests
import pandas as pd

from loguru import logger
from bs4 import BeautifulSoup
from datetime import datetime
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

with open(folder_path + "stages.json", "r") as f:
    stages_data = json.load(f)
    f.close()

stages_lookup = pd.DataFrame(stages_data["stages"])
logger.success("Loaded stages lookup table")

# ----------------------------------------------------------
# Create a lookup table if there are existing matches data
with open(folder_path + "matches.json", "r") as f:
    matches_data = json.load(f)
    f.close()

if len(matches_data["matches"]) != 0:
    logger.info("Existing matches data found. Creating a lookup table for match IDs.")
    all_matches_info = [match["matchInfo"] for match in matches_data["matches"]]
    matches_info_lookup = pd.DataFrame(all_matches_info)[
        ["id", "description", "localStartDate", "localStartTime"]
    ]

# ----------------------------------------------------------
# Determine which stage of the tournament is currently happening
current_stage = stages_lookup[
    (stages_lookup["startDate"] <= datetime.now().strftime("%Y-%m-%d"))
    & (stages_lookup["endDate"] >= datetime.now().strftime("%Y-%m-%d"))
]["name"].values[0]

logger.info(f"Current stage of the 2026 ASEAN Championship: {current_stage}")

matches = []

# Check if the matches json file contains data or not
# Making sure that the IDs don't get rotated when the file is updated with new matches

# Scrape match info and data from Wikipedia based on current stage
if current_stage == "Group Stage":
    for group in groups_lookup["name"]:
        request = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/html/2026_ASEAN_Championship_{group.replace(' ', '_')}",
            headers={"User-Agent": f"Match-Analysis-App/1.0 ({os.environ['EMAIL']})"},
        )

        soup = BeautifulSoup(request.text, "html.parser")
        all_matches = soup.find_all("section")[3].find_all("section")

        for match in all_matches:
            # Match info
            match_description = match.find("h3").text.strip()
            match_date = (
                match.find("time")
                .find_all("span", {"class": "bday dtstart published updated itvstart"})[
                    0
                ]
                .text.strip()
            )

            ## Fill in what's available
            match_info = {
                "id": (
                    (uuid.uuid4().hex)[:16]
                    if (len(matches_data["matches"]) == 0)
                    or (
                        matches_info_lookup.loc[
                            (matches_info_lookup["description"] == match_description)
                            & (matches_info_lookup["localStartDate"] == match_date)
                        ].empty
                    )
                    else (
                        matches_info_lookup.loc[
                            (matches_info_lookup["description"] == match_description)
                            & (matches_info_lookup["localStartDate"] == match_date),
                            "id",
                        ].values[0]
                    )
                ),
                "description": match_description,
                "localStartDate": match_date,
                "localStartTime": "",
                "stage": {
                    "id": stages_lookup[stages_lookup["name"] == "Group Stage"][
                        "id"
                    ].iloc[0],
                    "name": "Group Stage",
                    "group": {
                        "id": groups_lookup[groups_lookup["name"] == group]["id"].iloc[
                            0
                        ],
                        "name": group,
                    },
                },
                "contestants": [
                    {
                        "id": "",
                        "name": "",
                        "position": "home",
                    },
                    {
                        "id": "",
                        "name": "",
                        "position": "away",
                    },
                ],
                "venue": re.sub(
                    r"(\[[1-9]\])+",
                    "",
                    match.find("span", {"itemprop": "name address"}).text.strip(),
                ),
            }

            ## Extract the time string and clean it
            time_str = (
                match.find("time")
                .find("div", {"class": "ftime"})
                .text.replace("\xa0", " ")
                .replace(".", "")
                .strip()
            )

            ## Remove timezone if found
            if "UTC" in time_str:
                time_str = time_str.rsplit(" ", 1)[0].strip()

            ## Convert to 24-hour
            parsed_time = pd.to_datetime(time_str, format="%I:%M %p", errors="coerce")
            if pd.isna(parsed_time):
                parsed_time = pd.to_datetime(time_str, format="%H:%M", errors="coerce")

            time_24h = parsed_time.strftime("%H:%M") if not pd.isna(parsed_time) else ""
            match_info["localStartTime"] = time_24h

            ## Get the contestants
            home_team = match.find("h3").text.strip().split(" vs ")[0]
            away_team = match.find("h3").text.strip().split(" vs ")[1]

            match_info["contestants"][0]["name"] = home_team
            match_info["contestants"][1]["name"] = away_team

            ## Get contestant IDs
            ### General cases
            if (
                not teams_lookup[
                    (teams_lookup["fullName"] == home_team)
                    | (teams_lookup["shortName"] == home_team)
                ].empty
                and not teams_lookup[
                    (teams_lookup["fullName"] == away_team)
                    | (teams_lookup["shortName"] == away_team)
                ].empty
            ):
                home_team_info = teams_lookup[
                    (teams_lookup["fullName"] == home_team)
                    | (teams_lookup["shortName"] == home_team)
                ].reset_index(drop=True)
                away_team_info = teams_lookup[
                    (teams_lookup["fullName"] == away_team)
                    | (teams_lookup["shortName"] == away_team)
                ].reset_index(drop=True)
            ### Special cases
            # else:
            #     # Wikipedia name - FIFA-recognised name
            #     special_cases = {}
            #     home_team_info = teams_lookup[
            #         teams_lookup["fullName"]
            #         == special_cases.get(home_team, home_team)
            #         | teams_lookup["shortName"]
            #         == special_cases.get(home_team, home_team)
            #     ].reset_index(drop=True)
            #     away_team_info = teams_lookup[
            #         teams_lookup["fullName"]
            #         == special_cases.get(away_team, away_team)
            #         | teams_lookup["shortName"]
            #         == special_cases.get(away_team, away_team)
            #     ].reset_index(drop=True)

            match_info["contestants"][0]["id"] = (
                home_team_info.loc[0, "id"] if len(home_team_info) > 0 else None
            )
            match_info["contestants"][1]["id"] = (
                away_team_info.loc[0, "id"] if len(away_team_info) > 0 else None
            )

            # -------------------------------------------------------------------------
            # Match data
            match_data = {
                "matchStatus": (
                    "Fixture"
                    if "v" in match.find("th", {"class": "fscore"}).text.strip()
                    else "Played"
                ),
                "matchLengthMin": "",
                "matchLengthSec": "",
                "period": [
                    {
                        "id": 1,
                        "lengthMin": "",
                        "lengthSec": "",
                        "stoppageTime": "",  # In seconds
                    },
                    {
                        "id": 2,
                        "lengthMin": "",
                        "lengthSec": "",
                        "stoppageTime": "",  # In seconds
                    },
                ],
                "scores": {
                    "ht": {
                        "home": 0,
                        "away": 0,
                    },
                    "ft": {
                        "home": 0,
                        "away": 0,
                    },
                    "et": {
                        "home": 0,
                        "away": 0,
                    },
                    "total": {
                        "home": (
                            len(
                                match.find("td", {"class": "fhgoal"})
                                .text.strip()
                                .split("\n")
                            )
                            if match.find("td", {"class": "fhgoal"}).text != ""
                            else 0
                        ),
                        "away": (
                            len(
                                match.find("td", {"class": "fagoal"})
                                .text.strip()
                                .split("\n")
                            )
                            if match.find("td", {"class": "fagoal"}).text != ""
                            else 0
                        ),
                    },
                },
            }

            # -------------------------------------------------------------------------
            # Combine match info and data, and add to matches list
            matches.append({"matchInfo": match_info, "matchData": match_data})
else:
    request = requests.get(
        "https://en.wikipedia.org/api/rest_v1/page/html/2026_ASEAN_Championship_knockout_stage",
        headers={"User-Agent": f"Match-Analysis-App/1.0 ({os.environ['EMAIL']})"},
    )

    soup = BeautifulSoup(request.text, "html.parser")

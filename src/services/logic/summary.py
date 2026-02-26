# Compile a dictionary of match information and stats

# Imports
import json

from utils import load_json


def load_summary(file_paths: list) -> dict:
    """
    Retrieve the relevant info and stats for display.

    Args:
        file_path (list): List of file paths to search through for the relevant data.

    Returns:
        dict: The match summary data.
    """
    summary_dict = {
        "matchInfo": {
            "homeTeam": "",
            "awayTeam": "",
            "date": "",
            "competition": "",
            "tournamentCalendar": "",
            "stage": "",
            "periods": {
                "1H": {"lengthMin": "", "lengthSec": ""},
                "2H": {"lengthMin": "", "lengthSec": ""},
                "ET1": {"lengthMin": "", "lengthSec": ""},
                "ET2": {"lengthMin": "", "lengthSec": ""},
            },
            "scores": {
                "ht": {"home": "", "away": ""},
                "ft": {"home": "", "away": ""},
                "et": {"home": "", "away": ""},
                "penalties": {"home": "", "away": ""},
            },
        },
        "matchStats": {
            "home": {
                "formationUsed": "",
                "totalScoringAtt": "",
                "ontargetScoringAtt": "",
                "possessionPercentage": "",
                "totalPass": "",
                "accuratePass": "",
                "fkFoulLost": "",
                "totalYellowCard": "",
                "totalRedCard": "",
            },
            "away": {
                "formationUsed": "",
                "totalScoringAtt": "",
                "ontargetScoringAtt": "",
                "possessionPercentage": "",
                "totalPass": "",
                "accuratePass": "",
                "fkFoulLost": "",
                "totalYellowCard": "",
                "totalRedCard": "",
            },
        },
    }

    for file_path in file_paths:
        if "stats" in file_path.lower() and file_path.lower().endswith(".json"):
            # Load the file
            stats_file = load_json(file_path)

            # Extract match info
            match_info = stats_file.get("matchInfo", {})

            ## Team names
            home_team_id = ""
            away_team_id = ""
            contestants = match_info.get("contestant", [])
            for team in contestants:
                if team.get("position") == "home":
                    summary_dict["matchInfo"]["homeTeam"] = team.get("name", "")
                    home_team_id = team.get("id", "")
                elif team.get("position") == "away":
                    summary_dict["matchInfo"]["awayTeam"] = team.get("name", "")
                    away_team_id = team.get("id", "")

            ## Date
            summary_dict["matchInfo"]["date"] = match_info.get("localDate", "")

            ## Competition and stage
            competition_info = match_info.get("competition", {})
            summary_dict["matchInfo"]["competition"] = competition_info.get("name", "")

            tournament_calendar = match_info.get("tournamentCalendar", {})
            summary_dict["matchInfo"]["tournamentCalendar"] = tournament_calendar.get(
                "name", ""
            )

            stage_info = match_info.get("stage", {})
            summary_dict["matchInfo"]["stage"] = stage_info.get("name", "")

            # Extract match stats
            live_data = stats_file.get("liveData", {})
            match_details = live_data.get("matchDetails", {})

            ## Periods
            periods_info = match_details.get("period", [])
            for period in periods_info:
                if period.get("id") == 1:
                    ### First half
                    summary_dict["matchInfo"]["periods"]["1H"]["lengthMin"] = (
                        period.get("lengthMin", "")
                    )
                    summary_dict["matchInfo"]["periods"]["1H"]["lengthSec"] = (
                        period.get("lengthSec", "")
                    )
                elif period.get("id") == 2:
                    ### Second half
                    summary_dict["matchInfo"]["periods"]["2H"]["lengthMin"] = (
                        period.get("lengthMin", "")
                    )
                    summary_dict["matchInfo"]["periods"]["2H"]["lengthSec"] = (
                        period.get("lengthSec", "")
                    )
                elif period.get("id") == 3:
                    ### Extra time 1
                    summary_dict["matchInfo"]["periods"]["ET1"]["lengthMin"] = (
                        period.get("lengthMin", "")
                    )
                    summary_dict["matchInfo"]["periods"]["ET1"]["lengthSec"] = (
                        period.get("lengthSec", "")
                    )
                elif period.get("id") == 4:
                    ### Extra time 2
                    summary_dict["matchInfo"]["periods"]["ET2"]["lengthMin"] = (
                        period.get("lengthMin", "")
                    )
                    summary_dict["matchInfo"]["periods"]["ET2"]["lengthSec"] = (
                        period.get("lengthSec", "")
                    )

            ## Scores
            scores_info = match_details.get("scores", {})
            ### Half time
            summary_dict["matchInfo"]["scores"]["ht"]["home"] = scores_info.get(
                "ht", {}
            ).get("home", "")
            summary_dict["matchInfo"]["scores"]["ht"]["away"] = scores_info.get(
                "ht", {}
            ).get("away", "")
            ### Full time
            summary_dict["matchInfo"]["scores"]["ft"]["home"] = scores_info.get(
                "ft", {}
            ).get("home", "")
            summary_dict["matchInfo"]["scores"]["ft"]["away"] = scores_info.get(
                "ft", {}
            ).get("away", "")
            ### Extra time
            summary_dict["matchInfo"]["scores"]["et"]["home"] = scores_info.get(
                "et", {}
            ).get("home", "")
            summary_dict["matchInfo"]["scores"]["et"]["away"] = scores_info.get(
                "et", {}
            ).get("away", "")
            ### Penalties
            summary_dict["matchInfo"]["scores"]["penalties"]["home"] = scores_info.get(
                "pen", {}
            ).get("home", "")
            summary_dict["matchInfo"]["scores"]["penalties"]["away"] = scores_info.get(
                "pen", {}
            ).get("away", "")

            ## Match stats
            teams_stats = live_data.get("lineUp", [])
            for team in teams_stats:
                if team.get("contestantId") == home_team_id:
                    home_stats = team.get("stat", {})
                    for stat in home_stats:
                        if stat.get("type") == "formationUsed":
                            summary_dict["matchStats"]["home"]["formationUsed"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "totalScoringAtt":
                            summary_dict["matchStats"]["home"]["totalScoringAtt"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "ontargetScoringAtt":
                            summary_dict["matchStats"]["home"]["ontargetScoringAtt"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "possessionPercentage":
                            summary_dict["matchStats"]["home"][
                                "possessionPercentage"
                            ] = stat.get("value", "")
                        elif stat.get("type") == "totalPass":
                            summary_dict["matchStats"]["home"]["totalPass"] = stat.get(
                                "value", ""
                            )
                        elif stat.get("type") == "accuratePass":
                            summary_dict["matchStats"]["home"]["accuratePass"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "fkFoulLost":
                            summary_dict["matchStats"]["home"]["fkFoulLost"] = stat.get(
                                "value", ""
                            )
                        elif stat.get("type") == "totalYellowCard":
                            summary_dict["matchStats"]["home"]["totalYellowCard"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "totalRedCard":
                            summary_dict["matchStats"]["home"]["totalRedCard"] = (
                                stat.get("value", "")
                            )

                elif team.get("contestantId") == away_team_id:
                    away_stats = team.get("stat", {})
                    for stat in away_stats:
                        if stat.get("type") == "formationUsed":
                            summary_dict["matchStats"]["away"]["formationUsed"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "totalScoringAtt":
                            summary_dict["matchStats"]["away"]["totalScoringAtt"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "ontargetScoringAtt":
                            summary_dict["matchStats"]["away"]["ontargetScoringAtt"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "possessionPercentage":
                            summary_dict["matchStats"]["away"][
                                "possessionPercentage"
                            ] = stat.get("value", "")
                        elif stat.get("type") == "totalPass":
                            summary_dict["matchStats"]["away"]["totalPass"] = stat.get(
                                "value", ""
                            )
                        elif stat.get("type") == "accuratePass":
                            summary_dict["matchStats"]["away"]["accuratePass"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "fkFoulLost":
                            summary_dict["matchStats"]["away"]["fkFoulLost"] = stat.get(
                                "value", ""
                            )
                        elif stat.get("type") == "totalYellowCard":
                            summary_dict["matchStats"]["away"]["totalYellowCard"] = (
                                stat.get("value", "")
                            )
                        elif stat.get("type") == "totalRedCard":
                            summary_dict["matchStats"]["away"]["totalRedCard"] = (
                                stat.get("value", "")
                            )

    return summary_dict

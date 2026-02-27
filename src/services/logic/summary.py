# Compile a dictionary of match information and stats

# Imports
from utils import load_json

# Maps Opta stat types to display names. Formation is handled separately.
_STAT_TYPE_MAP = {
    "totalScoringAtt": "Shots attempted",
    "ontargetScoringAtt": "Shots on target",
    "possessionPercentage": "Possession %",
    "totalPass": "Passes made",
    "accuratePass": "Passes completed",
    "fkFoulLost": "Fouls committed",
    "totalYellowCard": "Yellow cards",
    "totalRedCard": "Red cards",
}

# Maps period IDs to their summary key
_PERIOD_ID_MAP = {1: "1H", 2: "2H", 3: "ET1", 4: "ET2"}

# Maps score keys in the data to summary keys
_SCORE_KEY_MAP = {"ht": "ht", "ft": "ft", "et": "et", "pen": "penalties"}


def _empty_team_stats() -> dict:
    return {display: "" for display in ["Formation"] + list(_STAT_TYPE_MAP.values())}


def _extract_team_stats(raw_stats: list) -> dict:
    """Parse a list of Opta stat objects into the summary stats dict."""
    result = _empty_team_stats()
    for stat in raw_stats:
        stat_type = stat.get("type")
        value = stat.get("value", "0")
        if stat_type == "formationUsed":
            result["Formation"] = "-".join(value)
        elif stat_type in _STAT_TYPE_MAP:
            result[_STAT_TYPE_MAP[stat_type]] = value
    return result


def load_summary(file_paths: list) -> dict:
    """
    Retrieve the relevant info and stats for display.

    Args:
        file_paths (list): List of file paths to search through for the relevant data.

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
                key: {"lengthMin": "", "lengthSec": ""}
                for key in _PERIOD_ID_MAP.values()
            },
            "scores": {
                key: {"home": "", "away": ""} for key in _SCORE_KEY_MAP.values()
            },
        },
        "matchStats": {
            "home": _empty_team_stats(),
            "away": _empty_team_stats(),
        },
    }

    for file_path in file_paths:
        if "stats" not in file_path.lower() or not file_path.lower().endswith(".json"):
            continue

        stats_file = load_json(file_path)
        match_info = stats_file.get("matchInfo", {})
        live_data = stats_file.get("liveData", {})
        match_details = live_data.get("matchDetails", {})

        # Team names and IDs
        home_team_id, away_team_id = "", ""
        for team in match_info.get("contestant", []):
            position = team.get("position")
            if position == "home":
                summary_dict["matchInfo"]["homeTeam"] = team.get("name", "")
                home_team_id = team.get("id", "")
            elif position == "away":
                summary_dict["matchInfo"]["awayTeam"] = team.get("name", "")
                away_team_id = team.get("id", "")

        # Date, competition, stage
        summary_dict["matchInfo"]["date"] = match_info.get("localDate", "")
        summary_dict["matchInfo"]["competition"] = match_info.get(
            "competition", {}
        ).get("name", "")
        summary_dict["matchInfo"]["tournamentCalendar"] = match_info.get(
            "tournamentCalendar", {}
        ).get("name", "")
        summary_dict["matchInfo"]["stage"] = match_info.get("stage", {}).get("name", "")

        # Periods
        for period in match_details.get("period", []):
            period_key = _PERIOD_ID_MAP.get(period.get("id"))
            if period_key:
                summary_dict["matchInfo"]["periods"][period_key]["lengthMin"] = (
                    period.get("lengthMin", "")
                )
                summary_dict["matchInfo"]["periods"][period_key]["lengthSec"] = (
                    period.get("lengthSec", "")
                )

        # Scores
        scores_info = match_details.get("scores", {})
        for data_key, summary_key in _SCORE_KEY_MAP.items():
            score = scores_info.get(data_key, {})
            summary_dict["matchInfo"]["scores"][summary_key]["home"] = score.get(
                "home", ""
            )
            summary_dict["matchInfo"]["scores"][summary_key]["away"] = score.get(
                "away", ""
            )

        # Team stats
        for team in live_data.get("lineUp", []):
            contestant_id = team.get("contestantId")
            if contestant_id == home_team_id:
                summary_dict["matchStats"]["home"] = _extract_team_stats(
                    team.get("stat", [])
                )
            elif contestant_id == away_team_id:
                summary_dict["matchStats"]["away"] = _extract_team_stats(
                    team.get("stat", [])
                )

    return summary_dict

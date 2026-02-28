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


def load_formation(stats_path: str, side: str = "home") -> dict:
    """
    Load the formation for the specified team.

    Args:
        stats_path (str): Path to the stats JSON file.
        side (str): "home" or "away" to specify which team's formation to load.

    Returns:
        dict: The team's formation and the corresponding player positions.
    """
    if side not in ("home", "away"):
        raise ValueError("Invalid side specified. Must be 'home' or 'away'.")

    stats_file = load_json(stats_path)
    match_info = stats_file.get("matchInfo", {})

    formation = {
        "formation": "",
        "kit": {
            "colour1": "",
            "colour2": "",
        },
        "players": {
            # playerId: {
            #     "shirtNumber": "",
            #     "matchName": "",
            #     "formationPlace": "",
            # }
        },
    }

    # Get the target team ID
    contestants = match_info.get("contestant", [])
    team_id = next(
        (team.get("id", "") for team in contestants if team.get("position") == side), ""
    )

    # Find the matching lineup entry
    live_data = stats_file.get("liveData", {})
    team_lineup = next(
        (t for t in live_data.get("lineUp", []) if t.get("contestantId") == team_id),
        None,
    )
    if not team_lineup:
        return {}

    # Extract formation
    formation["formation"] = team_lineup.get("formationUsed", [])

    # Extract kit colors
    formation["kit"]["colour1"] = team_lineup.get("kit", {}).get("colour1", "")
    formation["kit"]["colour2"] = team_lineup.get("kit", {}).get("colour2", "")

    # Extract player infos
    for player in team_lineup.get("player", []):
        if player.get("position", "") != "Substitute":
            player_id = player.get("playerId", "")
            formation["players"][player_id] = {
                "shirtNumber": player.get("shirtNumber", ""),
                "matchName": player.get("matchName", ""),
                "formationPlace": int(player.get("formationPlace", 0)),
            }

    return formation


def load_substitutions(stats_path: str, side: str = "home") -> list:
    """
    Load the substitutions for the specified team, sorted by time.

    Args:
        stats_path (str): Path to the stats JSON file.
        side (str): "home" or "away" to specify which team's substitutions to load.

    Returns:
        list[tuple]: List of (player_off_name, player_on_name, time_min_sec) tuples, sorted by time.
    """
    if side not in ("home", "away"):
        raise ValueError("Invalid side specified. Must be 'home' or 'away'.")

    stats_file = load_json(stats_path)
    match_info = stats_file.get("matchInfo", {})

    contestants = match_info.get("contestant", [])
    team_id = next(
        (team.get("id", "") for team in contestants if team.get("position") == side), ""
    )

    raw_subs = stats_file.get("liveData", {}).get("substitute", [])
    subs = [
        (
            sub.get("playerOffName", ""),
            sub.get("playerOnName", ""),
            sub.get("timeMinSec", ""),
        )
        for sub in raw_subs
        if sub.get("contestantId") == team_id and sub.get("timeMinSec")
    ]
    return sorted(
        subs,
        key=lambda x: (
            int(x[2].split(":")[0]),
            int(x[2].split(":")[1]) if ":" in x[2] else 0,
        ),
    )


def load_players(stats_path: str, side: str = "home", full_name: bool = True) -> dict:
    """
    Load the player list for the specified team.

    Args:
        stats_path (str): Path to the stats JSON file.
        side (str): "home" or "away" to specify which team's players to load.
        full_name (bool): Whether to return the player's full name (`shortFirstName` + `shortLastName`) or their match name.

    Returns:
        dict: Mapping of playerId to (shirtNumber, fullName).
    """
    if side not in ("home", "away"):
        raise ValueError("Invalid side specified. Must be 'home' or 'away'.")

    stats_file = load_json(stats_path)
    match_info = stats_file.get("matchInfo", {})

    # Resolve the target team ID
    team_ids = {}
    for team in match_info.get("contestant", []):
        position = team.get("position")
        if position in ("home", "away"):
            team_ids[position] = team.get("id", "")
    team_id = team_ids.get(side, "")

    # Find the matching lineup entry
    live_data = stats_file.get("liveData", {})
    team_lineup = next(
        (t for t in live_data.get("lineUp", []) if t.get("contestantId") == team_id),
        None,
    )
    if not team_lineup:
        return {}

    players = {}
    for player in team_lineup.get("player", []):
        player_stats = player.get("stat", [])
        has_played = any(stat.get("type") == "minsPlayed" for stat in player_stats)
        if has_played:
            player_id = player.get("playerId", "")
            shirt_number = player.get("shirtNumber", "")
            player_name = (
                f"{player.get('shortFirstName', '')} {player.get('shortLastName', '')}".strip()
                if full_name
                else player.get("matchName", "")
            )
            players[player_id] = (shirt_number, player_name)

    return players


def load_player_stats(stats_path: str, side: str = "home") -> dict:
    """
    Load the player stats for the specified team.

    Args:
        stats_path (str): Path to the stats JSON file.
        side (str): "home" or "away" to specify which team's player stats to load.

    Returns:
        dict: Mapping of playerId to their stats dictionary.
    """
    if side not in ("home", "away"):
        raise ValueError("Invalid side specified. Must be 'home' or 'away'.")

    # TODO: implement player stats loading
    pass

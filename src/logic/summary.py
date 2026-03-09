# Compile a dictionary of match information and stats

# Imports
import pandas as pd
from utils import (
    load_json,
    get_team_id,
    MATCH_STAT_TYPE_MAP,
    PERIOD_ID_MAP,
    SCORE_KEY_MAP,
    KEEPER_STAT_TYPE_MAP,
    OUTFIELD_STAT_TYPE_MAP,
)

# ---------------------------------------------------------------------------------------------
# Private helper functions and constants

# Canonical display order for position-side parts (Left < Right < Centre).
# This ensures "Centre/Right" renders as "RC..." rather than "CR...".
_SIDE_ORDER: dict[str, int] = {"Left": 0, "Right": 1, "Centre": 2}

# Sort order for player list: position group first, then left-to-right within group.
_POSITION_RANK: dict[str, int] = {
    "Goalkeeper": 0,
    "Defender": 1,
    "Midfielder": 2,
    "Striker": 3,
    "Substitute": 4,
}
_SORT_SIDE_ORDER: dict[str, int] = {
    "Left": 0,
    "Left/Centre": 1,
    "Centre/Left": 1,
    "Centre": 2,
    "Centre/Right": 3,
    "Right/Centre": 3,
    "Right": 4,
}

_SIDE_ERROR_MSG = "Invalid side specified. Must be 'home' or 'away'."


def _position_abbr(position: str, position_side: str) -> str:
    """
    Build a short position abbreviation from positionSide + position.

    Side parts (split by ``"/"``) are sorted into canonical order
    (Left → Right → Centre) so that e.g. ``"Centre/Right"`` and
    ``"Right/Centre"`` both produce the same abbreviation ``"RC"``.
    Each part then contributes its first letter, followed by the first
    letter of position.

    Examples::

        _position_abbr("Defender", "Left")          -> "LD"
        _position_abbr("Defender", "Left/Centre")   -> "LCD"
        _position_abbr("Defender", "Centre/Right")  -> "RCD"
        _position_abbr("Midfielder", "Centre")      -> "CM"
        _position_abbr("Forward", "Right/Centre")   -> "RCF"
    """
    parts = sorted(
        (p for p in position_side.split("/") if p),
        key=lambda p: _SIDE_ORDER.get(p, 99),
    )
    return "".join(p[0] for p in parts) + (position[0] if position else "")


def _empty_team_stats() -> dict:
    return dict.fromkeys(MATCH_STAT_TYPE_MAP.values(), "")


def _extract_team_stats(raw_stats: list) -> dict:
    """Parse a list of Opta stat objects into the summary stats dict."""
    result = _empty_team_stats()
    for stat in raw_stats:
        stat_type = stat.get("type")
        value = stat.get("value", "0")
        if stat_type == "formationUsed":
            result["Formation"] = "-".join(value)
        elif stat_type in MATCH_STAT_TYPE_MAP:
            result[MATCH_STAT_TYPE_MAP[stat_type]] = value
    return result


def _to_df(rows: list) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).set_index("#")


def _player_sort_key(player: dict) -> tuple:
    return (
        _POSITION_RANK.get(player.get("position", ""), 99),
        _SORT_SIDE_ORDER.get(player.get("positionSide", "") or "", 2),
    )


def _build_player_rows(players: list, stat_map: dict) -> list:
    """Build a list of stat row dicts for a group of players using the given stat map."""
    rows = []
    for player in players:
        raw = {s["type"]: int(s.get("value", 0)) for s in player.get("stat", [])}
        pos = player.get("position", "")
        row = {
            "#": player.get("shirtNumber", ""),
            "Name": f"{player.get('shortFirstName', '')} {player.get('shortLastName', '')}".strip(),
        }
        for stat_type, display_name in stat_map.items():
            if stat_type == "position":
                row[display_name] = (
                    "Sub"
                    if pos == "Substitute"
                    else _position_abbr(pos, player.get("positionSide", ""))
                )
            else:
                row[display_name] = raw.get(stat_type, 0)
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------------------------------
# Main data loading functions


def load_summary(stats_path: str) -> dict:
    """
    Retrieve the relevant info and stats for display.

    Args:
        stats_path (str): Path to the stats JSON file.

    Returns:
        dict: The match summary data.
    """
    stats_file = load_json(stats_path)
    match_info = stats_file.get("matchInfo", {})
    live_data = stats_file.get("liveData", {})
    match_details = live_data.get("matchDetails", {})

    teams = {t.get("position"): t for t in match_info.get("contestant", [])}
    home_team = teams.get("home", {})
    away_team = teams.get("away", {})

    lineup = {t.get("contestantId"): t for t in live_data.get("lineUp", [])}
    scores_info = match_details.get("scores", {})

    return {
        "matchInfo": {
            "homeTeam": home_team.get("name", ""),
            "awayTeam": away_team.get("name", ""),
            "date": match_info.get("localDate", ""),
            "competition": match_info.get("competition", {}).get("name", ""),
            "tournamentCalendar": match_info.get("tournamentCalendar", {}).get(
                "name", ""
            ),
            "stage": match_info.get("stage", {}).get("name", ""),
            "periods": {
                PERIOD_ID_MAP[p["id"]]: {
                    "lengthMin": p.get("lengthMin", ""),
                    "lengthSec": p.get("lengthSec", ""),
                }
                for p in match_details.get("period", [])
                if p.get("id") in PERIOD_ID_MAP
            },
            "scores": {
                display: {
                    "home": scores_info.get(raw, {}).get("home", ""),
                    "away": scores_info.get(raw, {}).get("away", ""),
                }
                for raw, display in SCORE_KEY_MAP.items()
            },
        },
        "matchStats": {
            "home": _extract_team_stats(
                lineup.get(home_team.get("id", ""), {}).get("stat", [])
            ),
            "away": _extract_team_stats(
                lineup.get(away_team.get("id", ""), {}).get("stat", [])
            ),
        },
    }


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
        raise ValueError(_SIDE_ERROR_MSG)

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
    team_id = get_team_id(match_info, side)

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


def load_kit_colors(stats_path: str, side: str = "home") -> dict:
    """
    Load the kit colors for the specified team from the stats JSON file.

    Args:
        stats_path (str): Path to the stats JSON file.
        side (str): "home" or "away". Default is "home".

    Returns:
        dict: Kit colors containing:
            - colour1 (str): Primary kit color (hex).
            - colour2 (str): Secondary kit color (hex); empty string if not present.
    """
    if side not in ("home", "away"):
        raise ValueError(_SIDE_ERROR_MSG)

    stats_file = load_json(stats_path)
    match_info = stats_file.get("matchInfo", {})

    team_id = get_team_id(match_info, side)

    team_lineup = next(
        (
            t
            for t in stats_file.get("liveData", {}).get("lineUp", [])
            if t.get("contestantId") == team_id
        ),
        None,
    )
    if not team_lineup:
        return {"colour1": "#FFFFFF", "colour2": ""}

    kit = team_lineup.get("kit", {})
    return {
        "colour1": kit.get("colour1", "#FFFFFF"),
        "colour2": kit.get("colour2", ""),
    }


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
        raise ValueError(_SIDE_ERROR_MSG)

    stats_file = load_json(stats_path)
    match_info = stats_file.get("matchInfo", {})

    team_id = get_team_id(match_info, side)

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
        raise ValueError(_SIDE_ERROR_MSG)

    stats_file = load_json(stats_path)
    match_info = stats_file.get("matchInfo", {})

    # Resolve the target team ID
    team_id = get_team_id(match_info, side)

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

    Players who have not recorded any minutes played are excluded.
    Results are sorted by position group (GK → Def → Mid → Fwd → Sub) then
    left-to-right within each group.

    Args:
        stats_path (str): Path to the stats JSON file.
        side (str): "home" or "away" to specify which team's player stats to load.

    Returns:
        dict: Two keys — ``"goalkeeper"`` and ``"outfield"`` — each containing a
        list of dicts, one per player, with ``"#"`` and ``"Name"`` followed by
        the display-name columns from the relevant stat type map.
    """
    if side not in ("home", "away"):
        raise ValueError(_SIDE_ERROR_MSG)

    stats_file = load_json(stats_path)
    match_info = stats_file.get("matchInfo", {})
    team_id = get_team_id(match_info, side)

    team_lineup = next(
        (
            t
            for t in stats_file.get("liveData", {}).get("lineUp", [])
            if t.get("contestantId") == team_id
        ),
        None,
    )
    if not team_lineup:
        return {"goalkeeper": [], "outfield": []}

    # Filter to players who saw game time, then sort by position group → side (L→R), subs last.
    played = sorted(
        (
            p
            for p in team_lineup.get("player", [])
            if any(s.get("type") == "minsPlayed" for s in p.get("stat", []))
        ),
        key=_player_sort_key,
    )

    goalkeepers = [p for p in played if p.get("position") == "Goalkeeper"]
    outfield = [p for p in played if p.get("position") != "Goalkeeper"]

    return {
        "goalkeeper": _to_df(_build_player_rows(goalkeepers, KEEPER_STAT_TYPE_MAP)),
        "outfield": _to_df(_build_player_rows(outfield, OUTFIELD_STAT_TYPE_MAP)),
    }

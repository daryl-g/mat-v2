# Logic to calculate team possession dominance and related stats

# Imports
from utils import load_json, get_team_id

# ---------------------------------------------------------------------------
# Private helper functions and constants

# Opta typeIds that represent a team being in possession of the ball.
_TOUCH_TYPE_IDS: frozenset[int] = frozenset({1, 2, 3, 13, 14, 15, 16, 42, 49})

# Periods where the home team attacks in the opposite direction (ends swap).
# Raw Opta coordinates are fixed-camera, so we rotate these 180° so that
# the home team always attacks left → right in the aggregate.
_SWAP_PERIODS: frozenset[int] = frozenset({2, 4})

# ---------------------------------------------------------------------------
# Public functions


def load_possession_stats(stats_path: str) -> dict:
    """
    Load possession stats for each team from an Opta match stats file.

    Args:
        stats_path (str): Path to the Opta match stats JSON file.

    Returns:
        dict: Two keys, ``"home"`` and ``"away"``, each containing a dict with the following keys and values:
            - ``possession_pct``: float, percentage of total match possession.
    """
    stats_file = load_json(stats_path)
    match_info = stats_file.get("matchInfo", {})

    home_id = get_team_id(match_info, "home")
    away_id = get_team_id(match_info, "away")

    possession_stats: dict = {
        "home": 0.0,
        "away": 0.0,
    }

    for team in stats_file.get("liveData", {}).get("lineUp", []):
        team_id = team.get("contestantId")
        if team_id not in (home_id, away_id):
            continue

        side = "home" if team_id == home_id else "away"
        poss_stat = next(
            (
                s
                for s in team.get("stat", [])
                if s.get("type") == "possessionPercentage"
            ),
            None,
        )
        possession_stats[side] = float(poss_stat["value"]) if poss_stat else 0.0

    return possession_stats


def load_possession_versus(event_path: str) -> dict:
    """
    Load touch coordinates from an Opta events file, normalised so that the
    home team always attacks left → right across all periods.

    Only on-ball events are included, any defensive actions or loose ball events are excluded.

    Half-time ends-swap is corrected: events from ``periodId`` 2 (and 4 for
    extra time) are rotated 180° — ``x → 100 - x``, ``y → 100 - y`` — so
    that both teams' attacking directions are consistent across the full match.

    Args:
        event_path (str): Path to the Opta events JSON file.

    Returns:
        dict: Two keys, ``"home"`` and ``"away"``, each containing a dict
        with ``"x"`` and ``"y"`` lists of floats representing touch coordinates::

            {
                "home": {"x": [...], "y": [...]},
                "away": {"x": [...], "y": [...]},
            }
    """
    events_file = load_json(event_path)
    match_info = events_file.get("matchInfo", {})

    home_id = get_team_id(match_info, "home")
    away_id = get_team_id(match_info, "away")

    touches: dict = {
        "home": {"x": [], "y": []},
        "away": {"x": [], "y": []},
    }

    for event in events_file.get("liveData", {}).get("event", []):
        period_id = event.get("periodId", 0)
        # In-play periods only (1=H1, 2=H2, 3=ET1, 4=ET2)
        if period_id not in (1, 2, 3, 4):
            continue

        type_id = event.get("typeId")
        if (type_id not in _TOUCH_TYPE_IDS) or (
            type_id == 4 and event.get("outcome") != 1
        ):
            continue

        contestant_id = event.get("contestantId")
        if contestant_id not in (home_id, away_id):
            continue

        x = float(event.get("x", 0))
        y = float(event.get("y", 0))

        side = "home" if contestant_id == home_id else "away"
        touches[side]["x"].append(x)
        touches[side]["y"].append(y)

    return touches


def load_field_tilt(event_path: str) -> dict:
    """
    Load the field tilt (angle of attack) for each team from an Opta events file.

    The field tilt is the ratio of each team's final third touches compared to the
    total final third touches in the match.

    Args:
        event_path (str): Path to the Opta events JSON file.

    Returns:
        dict: Two keys, ``"home"`` and ``"away"``, each containing a float
        representing that team's field tilt.
    """
    event_file = load_json(event_path)
    match_info = event_file.get("matchInfo", {})

    home_id = get_team_id(match_info, "home")
    away_id = get_team_id(match_info, "away")

    field_tilt: dict = {
        "home": 0.0,
        "away": 0.0,
    }

    # Load all touches and count how many are in the final third (x > 66.6) for each team
    for event in event_file.get("liveData", {}).get("event", []):
        type_id = event.get("typeId")
        if (type_id not in _TOUCH_TYPE_IDS) or (
            type_id == 4 and event.get("outcome") != 1
        ):
            continue

        contestant_id = event.get("contestantId")
        if contestant_id not in (home_id, away_id):
            continue

        x = float(event.get("x", 0))
        if x <= 66.6:
            continue

        side = "home" if contestant_id == home_id else "away"
        field_tilt[side] += 1

    total_final_third_touches = field_tilt["home"] + field_tilt["away"]
    if total_final_third_touches > 0:
        field_tilt["home"] /= total_final_third_touches
        field_tilt["away"] /= total_final_third_touches

    return field_tilt


def load_final_third_entries(event_path: str) -> dict:
    """
    Load the number of final third entries for each team from an Opta events file.

    A final third entry is defined as any passes, dribbles, or carries that
    end in the attacking third of the pitch, and starts from outside the final third.

    Args:
        event_path (str): Path to the Opta events JSON file.

    Returns:
        dict: Two keys, ``"home"`` and ``"away"``, each containing an integer
        representing that team's total number of final third entries.
    """
    return {"home": 0, "away": 0}  # Placeholder return value

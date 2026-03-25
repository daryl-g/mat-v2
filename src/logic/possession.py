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

# Opta qualifierIds for pass end coordinates (x and y as percentages 0–100).
_PASS_END_X_QUALIFIER: int = 140
_PASS_END_Y_QUALIFIER: int = 141

# Opta typeIds used to identify defensive actions.
# typeId 3 = take-on won, 4 = foul (qualifier 264 aerial foul excluded),
# 7 = tackle, 8 = interception, 45 = clearance, 50 = dispossessed, 54 = challenge/block.
_DEFENSIVE_TYPE_IDS: frozenset[int] = frozenset({3, 4, 7, 8, 45, 50, 54})

# Opta qualifier that marks an aerial foul — exclude from defensive actions.
_AERIAL_FOUL_QUALIFIER: int = 264

# Opta x-coordinate threshold for the attacking final third (0–100 scale).
_FINAL_THIRD_X: float = 66.6

# Opta x/y boundaries for the penalty box (attacking end, 0–100 scale).
_BOX_X: float = 83.0
_BOX_Y_MIN: float = 21.1
_BOX_Y_MAX: float = 78.9

# Opta typeIds for possession-winning events used in high turnover detection.
# typeId 7 = tackle won (outcome=1), 8 = interception, 49 = loose ball recovery.
_HIGH_TURNOVER_TYPE_IDS: frozenset[int] = frozenset({7, 8, 49})

# x-coordinate threshold for high turnovers: possession won within 40 m of the
# opposition's goal (Opta 0–100 scale, attacking end is x=100).
_HIGH_TURNOVER_X: float = 60.0

# Opta typeIds representing shots, used to link high turnovers to subsequent attacks.
_SHOT_TYPE_IDS: frozenset[int] = frozenset({13, 14, 15, 16})

# Seconds after a high turnover within which a shot/goal is attributed to it.
_HIGH_TURNOVER_WINDOW_SECS: int = 15

# ---------------------------------------------------------------------------
# Private helper functions


def _pass_end_coords(event: dict) -> tuple[float, float] | None:
    """Return (end_x, end_y) from pass end qualifiers, or None if absent."""
    qmap = {q["qualifierId"]: q.get("value") for q in event.get("qualifier", [])}
    ex = qmap.get(_PASS_END_X_QUALIFIER)
    ey = qmap.get(_PASS_END_Y_QUALIFIER)
    return (float(ex), float(ey)) if ex is not None and ey is not None else None


def _final_third_entry_info(event: dict) -> dict | None:
    """Return entry info dict or None if the event doesn't cross into the final third."""
    x = float(event.get("x", 0))
    y = float(event.get("y", 0))
    if event.get("typeId") == 1:
        coords = _pass_end_coords(event)
        if coords is not None and x <= _FINAL_THIRD_X and coords[0] > _FINAL_THIRD_X:
            return {"start_x": x, "start_y": y, "x": coords[0], "y": coords[1], "type_id": 1}
        return None
    # typeId 3 — take-on: use event location as end-point proxy
    if x > _FINAL_THIRD_X:
        return {"start_x": x, "start_y": y, "x": x, "y": y, "type_id": 3}
    return None


def _box_entry_info(event: dict) -> dict | None:
    """Return entry info dict or None if the event doesn't cross into the penalty box."""
    x = float(event.get("x", 0))
    y = float(event.get("y", 0))
    if event.get("typeId") == 1:
        coords = _pass_end_coords(event)
        if (
            coords is not None
            and x <= _BOX_X
            and coords[0] > _BOX_X
            and _BOX_Y_MIN <= coords[1] <= _BOX_Y_MAX
        ):
            return {"start_x": x, "start_y": y, "x": coords[0], "y": coords[1], "type_id": 1}
        return None
    # typeId 3 — take-on: use event location as proxy
    if x > _BOX_X and _BOX_Y_MIN <= y <= _BOX_Y_MAX:
        return {"start_x": x, "start_y": y, "x": x, "y": y, "type_id": 3}
    return None


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
    Load final third entry coordinates for each team from an Opta events file.

    A final third entry is defined as any successful pass or take-on (dribble)
    whose end point crosses into the attacking third of the pitch from outside it.

    Args:
        event_path (str): Path to the Opta events JSON file.

    Returns:
        dict: Two keys, ``"home"`` and ``"away"``, each containing a dict
        with ``"x"``, ``"y"``, ``"start_x"``, ``"start_y"``, and ``"type_id"``
        lists representing the end-point and start-point of each entry::

            {
                "home": {"x": [...], "y": [...], "start_x": [...], "start_y": [...], "type_id": [...]},
                "away": {...},
            }

        ``type_id`` is ``1`` for passes and ``3`` for take-ons (no true end
        coordinates for take-ons — start equals end).
    """
    event_file = load_json(event_path)
    match_info = event_file.get("matchInfo", {})

    home_id = get_team_id(match_info, "home")
    away_id = get_team_id(match_info, "away")

    entries: dict = {
        "home": {"x": [], "y": [], "start_x": [], "start_y": [], "type_id": []},
        "away": {"x": [], "y": [], "start_x": [], "start_y": [], "type_id": []},
    }

    for event in event_file.get("liveData", {}).get("event", []):
        if event.get("periodId", 0) not in (1, 2, 3, 4):
            continue
        if event.get("typeId") not in (1, 3):
            continue
        if event.get("outcome") != 1:
            continue
        contestant_id = event.get("contestantId")
        if contestant_id not in (home_id, away_id):
            continue
        info = _final_third_entry_info(event)
        if info is not None:
            side = "home" if contestant_id == home_id else "away"
            entries[side]["x"].append(info["x"])
            entries[side]["y"].append(info["y"])
            entries[side]["start_x"].append(info["start_x"])
            entries[side]["start_y"].append(info["start_y"])
            entries[side]["type_id"].append(info["type_id"])

    return entries

def load_box_entries(event_path: str) -> dict:
    """
    Load box entry coordinates for each team from an Opta events file.

    A box entry is defined as any successful pass or take-on (dribble) whose
    end point crosses into the penalty box from outside it.

    Args:
        event_path (str): Path to the Opta events JSON file.

    Returns:
        dict: Two keys, ``"home"`` and ``"away"``, each containing a dict
        with ``"x"``, ``"y"``, ``"start_x"``, ``"start_y"``, and ``"type_id"``
        lists representing the end-point and start-point of each entry::

            {
                "home": {"x": [...], "y": [...], "start_x": [...], "start_y": [...], "type_id": [...]},
                "away": {...},
            }

        ``type_id`` is ``1`` for passes and ``3`` for take-ons.
    """
    event_file = load_json(event_path)
    match_info = event_file.get("matchInfo", {})

    home_id = get_team_id(match_info, "home")
    away_id = get_team_id(match_info, "away")

    entries: dict = {
        "home": {"x": [], "y": [], "start_x": [], "start_y": [], "type_id": []},
        "away": {"x": [], "y": [], "start_x": [], "start_y": [], "type_id": []},
    }

    for event in event_file.get("liveData", {}).get("event", []):
        if event.get("periodId", 0) not in (1, 2, 3, 4):
            continue
        if event.get("typeId") not in (1, 3):
            continue
        if event.get("outcome") != 1:
            continue
        contestant_id = event.get("contestantId")
        if contestant_id not in (home_id, away_id):
            continue
        info = _box_entry_info(event)
        if info is not None:
            side = "home" if contestant_id == home_id else "away"
            entries[side]["x"].append(info["x"])
            entries[side]["y"].append(info["y"])
            entries[side]["start_x"].append(info["start_x"])
            entries[side]["start_y"].append(info["start_y"])
            entries[side]["type_id"].append(info["type_id"])

    return entries

def load_defensive_actions(event_path: str) -> dict:
    """
    Load defensive action coordinates and types for each team from an Opta events file.

    Defensive actions include take-ons won (typeId 3), fouls (typeId 4, excluding
    aerial fouls marked by qualifier 264), tackles (typeId 7), interceptions
    (typeId 8), clearances (typeId 45), dispossessions (typeId 50), and
    challenges/blocks (typeId 54).

    Args:
        event_path (str): Path to the Opta events JSON file.

    Returns:
        dict: Two keys, ``"home"`` and ``"away"``, each containing a dict
        with ``"x"``, ``"y"``, ``"type_id"``, and ``"outcome"`` lists::

            {
                "home": {"x": [...], "y": [...], "type_id": [...], "outcome": [...]},
                "away": {...},
            }

        For ``typeId 4`` (fouls), ``outcome=0`` means the team committed the
        foul and ``outcome=1`` means the team won it.
    """
    event_file = load_json(event_path)
    match_info = event_file.get("matchInfo", {})

    home_id = get_team_id(match_info, "home")
    away_id = get_team_id(match_info, "away")

    actions: dict = {
        "home": {"x": [], "y": [], "type_id": [], "outcome": []},
        "away": {"x": [], "y": [], "type_id": [], "outcome": []},
    }

    for event in event_file.get("liveData", {}).get("event", []):
        if event.get("periodId", 0) not in (1, 2, 3, 4):
            continue

        type_id = event.get("typeId")
        if type_id not in _DEFENSIVE_TYPE_IDS:
            continue

        # Exclude aerial fouls (qualifier 264) from the foul type
        if type_id == 4 and any(
            q.get("qualifierId") == _AERIAL_FOUL_QUALIFIER
            for q in event.get("qualifier", [])
        ):
            continue

        # Exclude fouls won (outcome=1) — not a defensive action by the team
        if type_id == 4 and event.get("outcome") == 1:
            continue

        contestant_id = event.get("contestantId")
        if contestant_id not in (home_id, away_id):
            continue

        side = "home" if contestant_id == home_id else "away"
        actions[side]["x"].append(float(event.get("x", 0)))
        actions[side]["y"].append(float(event.get("y", 0)))
        actions[side]["type_id"].append(type_id)
        actions[side]["outcome"].append(event.get("outcome", 0))

    return actions


def _event_elapsed(event: dict) -> int:
    """Return total elapsed seconds for an event (timeMin * 60 + timeSec)."""
    return event.get("timeMin", 0) * 60 + event.get("timeSec", 0)


def _scan_sequence(
    events: list,
    start_idx: int,
    contestant_id: str,
    period: int,
    t0: int,
) -> tuple[bool, bool]:
    """
    Scan events after ``start_idx`` to detect whether the given contestant
    had a shot or goal within ``_HIGH_TURNOVER_WINDOW_SECS`` seconds in the
    same period.

    Returns:
        tuple[bool, bool]: (led_to_shot, led_to_goal)
    """
    led_to_shot = False
    led_to_goal = False
    for next_event in events[start_idx:]:
        if next_event.get("periodId") != period:
            break
        if _event_elapsed(next_event) - t0 > _HIGH_TURNOVER_WINDOW_SECS:
            break
        if next_event.get("contestantId") == contestant_id:
            next_type = next_event.get("typeId")
            if next_type in _SHOT_TYPE_IDS:
                led_to_shot = True
                if next_type == 16:
                    led_to_goal = True
                    break
    return led_to_shot, led_to_goal


def load_high_turnovers(event_path: str) -> dict:
    """
    Load high turnover events for each team from an Opta events file.

    A high turnover is possession won (tackle won, interception, or loose ball
    recovery with outcome=1) whose x-coordinate is above 60 on the Opta 0–100
    scale — roughly 40 metres from the opposition's goal.

    Each event is tagged whether it was followed by a shot or a goal by the
    same team within ``_HIGH_TURNOVER_WINDOW_SECS`` seconds in the same period.

    Args:
        event_path (str): Path to the Opta events JSON file.

    Returns:
        dict: Two keys, ``"home"`` and ``"away"``, each containing a dict
        with ``"x"``, ``"y"``, ``"led_to_shot"``, and ``"led_to_goal"`` lists::

            {
                "home": {
                    "x": [...], "y": [...],
                    "led_to_shot": [bool, ...], "led_to_goal": [bool, ...],
                },
                "away": {...},
            }
    """
    event_file = load_json(event_path)
    match_info = event_file.get("matchInfo", {})

    home_id = get_team_id(match_info, "home")
    away_id = get_team_id(match_info, "away")

    events = event_file.get("liveData", {}).get("event", [])

    turnovers: dict = {
        "home": {"x": [], "y": [], "led_to_shot": [], "led_to_goal": []},
        "away": {"x": [], "y": [], "led_to_shot": [], "led_to_goal": []},
    }

    for i, event in enumerate(events):
        if event.get("periodId", 0) not in (1, 2, 3, 4):
            continue
        if event.get("typeId") not in _HIGH_TURNOVER_TYPE_IDS:
            continue
        if event.get("outcome", 0) != 1:
            continue

        contestant_id = event.get("contestantId")
        if contestant_id not in (home_id, away_id):
            continue

        x = float(event.get("x", 0))
        if x <= _HIGH_TURNOVER_X:
            continue

        led_to_shot, led_to_goal = _scan_sequence(
            events, i + 1, contestant_id, event.get("periodId"), _event_elapsed(event)
        )

        side = "home" if contestant_id == home_id else "away"
        turnovers[side]["x"].append(x)
        turnovers[side]["y"].append(float(event.get("y", 0)))
        turnovers[side]["led_to_shot"].append(led_to_shot)
        turnovers[side]["led_to_goal"].append(led_to_goal)

    return turnovers
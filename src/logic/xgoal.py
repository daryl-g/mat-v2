# Process and logic functions for the xgoal file

# Imports
import pandas as pd
from utils import load_json

# ---------------------------------------------------------------------------
# Opta event type IDs for shots
_TYPE_BLOCKED = 12
_TYPE_GOAL = 16
_TYPE_OWN_GOAL = 17  # remapped internally when own-goal qualifier is found

# Opta qualifier IDs
_QUAL_OWN_GOAL = 28
_QUAL_XG = 321
_QUAL_XGOT = 322
_QUAL_BLOCKED = 82

# Default gap width (minutes) inserted between halves in the xG timeline
_GAP_WIDTH = 2

# Opta's standard xG value for a penalty — used to detect and strip penalty xG
PEN_XG = 0.7884


# ---------------------------------------------------------------------------
# Private helpers


def _get_team_id(match_info: dict, side: str) -> str:
    """Return the Opta contestant ID for the requested side."""
    return next(
        (
            c.get("id", "")
            for c in match_info.get("contestant", [])
            if c.get("position") == side
        ),
        "",
    )


def _parse_qualifiers(qualifiers: list[dict]) -> dict:
    """Return a flat {qualifierId: value} mapping for a single event's qualifiers."""
    return {q["qualifierId"]: q.get("value") for q in qualifiers}


# ---------------------------------------------------------------------------
# Public functions


def load_shots(xgoal_path: str, side: str = "home") -> list[dict]:
    """
    Load shot events for the specified team from an Opta xgoal JSON file.

    Returns all fields required by both the xG timeline (xg, xgot, time) and
    the shot map (x, y coordinates) so callers can ignore whichever they don't need.

    Args:
        xgoal_path (str): Path to the Opta xgoal JSON file.
        side (str): "home" or "away". Default is "home".

    Returns:
        list[dict]: One dict per shot, containing:
            - period_id  (int)  : Period the shot was taken in (1–4).
            - time_min   (int)  : Actual minute the shot was taken.
            - shot_type  (int)  : Normalised Opta type ID:
                                  12 = blocked, 14 = post, 15 = on target,
                                  16 = goal, 17 = own goal.
            - is_own_goal (bool): True when the own-goal qualifier (28) is present.
            - player_name (str) : Name of the player who took the shot.
            - scorer_name (str) : Annotated name for goal events only;
                                  includes " (OG)" suffix for own goals.
            - xg   (float): xG value (qualifier 321); 0.0 if absent.
            - xgot (float): xGOT value (qualifier 322); 0.0 if absent.
            - x    (float): Opta x-coordinate of the shot origin.
            - y    (float): Opta y-coordinate of the shot origin.
    """
    if side not in ("home", "away"):
        raise ValueError("Invalid side specified. Must be 'home' or 'away'.")

    xgoal_data = load_json(xgoal_path)
    team_id = _get_team_id(xgoal_data.get("matchInfo", {}), side)

    shots = []
    for event in xgoal_data.get("liveData", {}).get("event", []):
        # Periods beyond 4 means penalty shootout — stop processing
        if event.get("periodId", 0) > 4:
            break

        if event.get("contestantId") != team_id:
            continue

        quals = _parse_qualifiers(event.get("qualifier", []))

        is_own_goal = _QUAL_OWN_GOAL in quals
        shot_type = event.get("typeId")

        # Remap: blocked shot takes priority over base type
        if _QUAL_BLOCKED in quals:
            shot_type = _TYPE_BLOCKED

        # Remap: own goals become a distinct type for downstream rendering
        if is_own_goal and shot_type == _TYPE_GOAL:
            shot_type = _TYPE_OWN_GOAL

        if shot_type == _TYPE_GOAL:
            scorer_name = event.get("playerName", "")
        elif shot_type == _TYPE_OWN_GOAL:
            scorer_name = event.get("playerName", "") + " (OG)"
        else:
            scorer_name = ""

        shots.append(
            {
                "period_id": event.get("periodId"),
                "time_min": event.get("timeMin"),
                "shot_type": shot_type,
                "is_own_goal": is_own_goal,
                "player_name": event.get("playerName", ""),
                "scorer_name": scorer_name,
                "xg": float(quals.get(_QUAL_XG) or 0),
                "xgot": float(quals.get(_QUAL_XGOT) or 0),
                "x": float(event.get("x", 0)),
                "y": float(event.get("y", 0)),
            }
        )

    return shots


def load_xg_timeline(xgoal_path: str, configs: dict) -> pd.DataFrame:
    """
    Build the xG timeline DataFrame from an Opta xgoal JSON file.

    Processes all shot events for both teams chronologically, computing
    the display minute (adjusted for half-time gaps) and accumulating
    running xG totals.  The first row is always a (0, 0) baseline so
    the step chart starts from the origin.

    Args:
        xgoal_path (str): Path to the Opta xgoal JSON file.
        configs (dict): Configs dict returned by ``load_xgoal_configs``.

    Returns:
        pd.DataFrame: One row per shot event (plus a baseline row), with
        columns:
            - minute        (float): Display minute (gap-adjusted)
            - real_minute   (int)  : Actual match minute
            - period_id     (int)  : Period 1-4
            - home_scorer   (str)  : Scorer name for home goals, else ""
            - away_scorer   (str)  : Scorer name for away goals, else ""
            - home_xg_shot  (float): xG of this shot (home); 0 if away shot
            - away_xg_shot  (float): xG of this shot (away); 0 if home shot
            - home_xg       (float): Running cumulative xG — home team
            - away_xg       (float): Running cumulative xG — away team
            - home_xgot     (float): xGOT of this shot (home); 0 if away shot
            - away_xgot     (float): xGOT of this shot (away); 0 if home shot
            - shot_type     (int)  : Normalised type (12/14/15/16/26)
    """
    xgoal_data = load_json(xgoal_path)
    match_info = xgoal_data.get("matchInfo", {})
    home_id = _get_team_id(match_info, "home")

    gap = configs["gap_width"]
    fht = configs["first_half_time"]
    sht = configs["second_half_time"]
    fet = configs["first_extra_time"]

    # Cumulative offset added to raw timeMin to get the display minute.
    # Each completed period contributes its stoppage time and one gap.
    _period_offset = {
        1: 0,
        2: (fht - 45) + gap,
        3: (fht - 45) + gap + (sht - 45) + gap,
        4: (fht - 45) + gap + (sht - 45) + gap + (fet - 15) + gap,
    }

    # Baseline row — ensures the step chart starts at (0, 0)
    rows = [
        {
            "minute": 0,
            "real_minute": 0,
            "period_id": 0,
            "home_scorer": "",
            "away_scorer": "",
            "home_xg_shot": 0.0,
            "away_xg_shot": 0.0,
            "home_xg": 0.0,
            "away_xg": 0.0,
            "home_xgot": 0.0,
            "away_xgot": 0.0,
            "shot_type": 0,
        }
    ]

    home_xg_total = 0.0
    away_xg_total = 0.0

    for event in xgoal_data.get("liveData", {}).get("event", []):
        period_id = event.get("periodId", 0)
        if period_id > 4:
            break

        quals = _parse_qualifiers(event.get("qualifier", []))
        is_own_goal = _QUAL_OWN_GOAL in quals
        is_home = event.get("contestantId") == home_id

        shot_type = event.get("typeId")
        if _QUAL_BLOCKED in quals:
            shot_type = _TYPE_BLOCKED

        # Own goals use type 26 in the timeline (no xG value)
        if is_own_goal:
            shot_type = 26
            xg_val = 0.0
            xgot_val = 0.0
        else:
            xg_val = float(quals.get(_QUAL_XG) or 0)
            xgot_val = float(quals.get(_QUAL_XGOT) or 0)

        # Accumulate running totals and split per-shot values by side
        if is_home and not is_own_goal:
            home_xg_total += xg_val
            home_xg_shot, away_xg_shot = xg_val, 0.0
            home_xgot, away_xgot = xgot_val, 0.0
        elif not is_home and not is_own_goal:
            away_xg_total += xg_val
            home_xg_shot, away_xg_shot = 0.0, xg_val
            home_xgot, away_xgot = 0.0, xgot_val
        else:  # own goal — no xG contribution
            home_xg_shot, away_xg_shot = 0.0, 0.0
            home_xgot, away_xgot = 0.0, 0.0

        # Build scorer annotation
        player = event.get("playerName", "")
        if shot_type == _TYPE_GOAL:
            home_scorer, away_scorer = (player, "") if is_home else ("", player)
        elif shot_type == 26:
            # Own goal: annotate on the *conceding* team's side
            if is_home:
                home_scorer, away_scorer = "", player + " (OG)"
            else:
                home_scorer, away_scorer = player + " (OG)", ""
        else:
            home_scorer, away_scorer = "", ""

        display_minute = event.get("timeMin", 0) + _period_offset.get(period_id, 0)

        rows.append(
            {
                "minute": display_minute,
                "real_minute": event.get("timeMin", 0),
                "period_id": period_id,
                "home_scorer": home_scorer,
                "away_scorer": away_scorer,
                "home_xg_shot": home_xg_shot,
                "away_xg_shot": away_xg_shot,
                "home_xg": home_xg_total,
                "away_xg": away_xg_total,
                "home_xgot": home_xgot,
                "away_xgot": away_xgot,
                "shot_type": shot_type,
            }
        )

    return pd.DataFrame(rows)


def load_axis_configs(xg_data: pd.DataFrame, configs: dict) -> dict:
    """
    Derive chart axis parameters from an xG timeline DataFrame and match configs.

    Computes y-axis tick positions/labels (scaled to the match's peak xG),
    x-axis tick positions/labels (accounting for stoppage time and half-time
    gaps), and key timing values used by the plotting function.

    Args:
        xg_data (pd.DataFrame): DataFrame returned by ``load_xg_timeline``.
        configs (dict): Configs dict returned by ``load_xgoal_configs``.

    Returns:
        dict: Axis configuration values, containing:
            - max_xg         (float)      : Peak cumulative xG (rounded to 1 dp)
            - graph_end_time (float)      : Display minute of the match end
            - last_shot      (float)      : Display minute of the last shot
            - is_extra_time  (bool)       : True if the match went to ET
            - y_times        (list[float]): Y-axis tick positions
            - y_labels       (list[str])  : Y-axis tick labels
            - x_times        (list[float]): X-axis tick positions
            - x_labels       (list[str])  : X-axis tick labels
    """
    fht = configs["first_half_time"]
    sht = configs["second_half_time"]
    fet = configs["first_extra_time"]
    set_ = configs["second_extra_time"]
    gap = configs["gap_width"]
    period_count = configs["period_count"]

    raw_max = max(xg_data["home_xg"].iloc[-1], xg_data["away_xg"].iloc[-1])

    # Pick a round step size so we always have 6-10 ticks
    for step in (0.25, 0.5, 1.0, 1.5, 2.0):
        axis_top = step * (int(raw_max / step) + 2)  # at least 1 step above max
        tick_count = int(axis_top / step) + 1
        if tick_count <= 10:
            break

    max_xg = round(axis_top, 2)
    y_times = [round(i * step, 4) for i in range(tick_count)]
    y_labels = [str(int(v)) if v == int(v) else str(v) for v in y_times]

    match_length = fht + sht + fet + set_
    is_extra_time = set_ > 0
    # Number of gaps = number of period boundaries = period_count - 1
    graph_end_time = match_length + (period_count - 1) * gap
    last_shot = float(xg_data["minute"].iloc[-1])

    # Precomputed display-minute positions of period boundaries
    tmp1st = fht
    tmp2nd = fht + gap + sht
    tmp1et = fht + gap + sht + gap + fet

    # boundary_pairs: (gap_start, gap_end) in display minutes
    boundary_pairs = [(tmp1st, tmp1st + gap)]
    if is_extra_time:
        boundary_pairs += [
            (tmp2nd, tmp2nd + gap),
            (tmp1et, tmp1et + gap),
        ]

    if not is_extra_time:
        x_times = [
            0,
            15,
            30,
            45,
            fht,
            fht + gap,
            fht + 15 + gap,
            fht + 30 + gap,
            fht + 45 + gap,
            graph_end_time,
        ]
        x_labels = [
            "",
            "15",
            "30",
            "45",
            "",
            "45",
            "60",
            "75",
            "90",
            str(45 + sht),
        ]
    else:
        # Labels use the real match minutes at each tick position
        actual_match_end = 90 + fet + set_
        x_times = [
            0,
            15,
            30,
            45,
            tmp1st,
            tmp1st + gap,
            tmp1st + 15 + gap,
            tmp1st + 30 + gap,
            tmp1st + 45 + gap,
            tmp2nd,
            tmp2nd + gap,
            tmp2nd + 15 + gap,
            tmp1et,
            tmp1et + gap,
            graph_end_time,
        ]
        x_labels = [
            "",
            "15",
            "30",
            "45",
            "",
            "45",
            "60",
            "75",
            str(45 + sht),
            "",
            "90",
            "105",
            "",
            "105",
            str(actual_match_end),
        ]

    return {
        "max_xg": max_xg,
        "graph_end_time": graph_end_time,
        "last_shot": last_shot,
        "is_extra_time": is_extra_time,
        "boundary_pairs": boundary_pairs,
        "y_times": y_times,
        "y_labels": y_labels,
        "x_times": x_times,
        "x_labels": x_labels,
    }


def load_minutes(events_path: str) -> dict:
    """
    Load match period length information from an Opta events JSON file.

    Period lengths are derived from the actual period-end events (typeId 30)
    so that injury/stoppage time is included.  Defaults of 45' per half are
    used for any period whose end event is not present in the file.

    Args:
        events_path (str): Path to the Opta events JSON file.

    Returns:
        dict: Configuration values for building an xG timeline, containing:
            - first_half_time   (int) : Length of the 1st half in minutes.
            - second_half_time  (int) : Length of the 2nd half in minutes.
            - first_extra_time  (int) : Length of ET 1st half (0 if no ET).
            - second_extra_time (int) : Length of ET 2nd half (0 if no ET).
            - period_count      (int) : Total number of periods played.
            - gap_width         (int) : Gap in display-minutes between halves.
    """
    events_data = load_json(events_path)
    match_info = events_data.get("matchInfo", {})
    period_count = int(match_info.get("numberOfPeriods", 2))

    # Defaults (standard match with no stoppage time)
    period_end_minutes = {1: 45, 2: 90, 3: 105, 4: 120}

    for event in events_data.get("liveData", {}).get("event", []):
        if event.get("typeId") == 30:
            pid = event.get("periodId")
            if pid in period_end_minutes:
                period_end_minutes[pid] = int(
                    event.get("timeMin", period_end_minutes[pid])
                )

    first_half_time = period_end_minutes[1]
    second_half_time = period_end_minutes[2] - 45
    first_extra_time = max(0, period_end_minutes[3] - 90) if period_count > 2 else 0
    second_extra_time = max(0, period_end_minutes[4] - 105) if period_count > 3 else 0

    return {
        "first_half_time": first_half_time,
        "second_half_time": second_half_time,
        "first_extra_time": first_extra_time,
        "second_extra_time": second_extra_time,
        "period_count": period_count,
        "gap_width": _GAP_WIDTH,
    }


def summarise_shots(shots: list) -> dict:
    """
    Aggregate shot events into per-outcome counts and non-penalty xG totals.

    Args:
        shots (list[dict]): Shot dicts from load_shots().

    Returns:
        dict: One entry per outcome plus ``penalties``, ``own_goals``, and
        ``total`` entries, each being a dict with ``count`` (int) and
        ``xg`` (float) keys::

            {
                "goals":      {"count": int, "xg": float},  # non-pen, non-OG goals
                "saved":      {"count": int, "xg": float},
                "post":       {"count": int, "xg": float},
                "blocked":    {"count": int, "xg": float},
                "off_target": {"count": int, "xg": float},
                "penalties":  {"count": int, "xg": float},  # all penalty attempts
                "own_goals":  {"count": int, "xg": 0.0},   # always 0 xG
                "total":      {"count": int, "xg": float},  # npxG (no pen xG)
            }

        Penalties are detected by ``abs(xg - PEN_XG) < 0.001`` and isolated
        into their own bucket so ``total.xg`` reflects non-penalty xG only,
        matching the npxG label shown on the xG timeline.
    """
    buckets = {
        k: {"count": 0, "xg": 0.0}
        for k in (
            "goals",
            "saved",
            "post",
            "blocked",
            "off_target",
            "penalties",
            "own_goals",
            "total",
        )
    }
    for shot in shots:
        t = shot["shot_type"]
        xg = float(shot["xg"])
        buckets["total"]["count"] += 1

        # Own goals: isolated bucket, no xG contribution
        if t == _TYPE_OWN_GOAL:
            buckets["own_goals"]["count"] += 1
            continue

        # Penalties: all attempts (scored or not) detected by xG threshold
        if abs(xg - PEN_XG) < 0.001:
            buckets["penalties"]["count"] += 1
            buckets["penalties"]["xg"] += xg
            continue

        # Regular open-play shots
        if t == _TYPE_GOAL:
            key = "goals"
        elif t == 15:
            key = "saved"
        elif t == 14:
            key = "post"
        elif t == _TYPE_BLOCKED:
            key = "blocked"
        else:
            key = "off_target"
        buckets[key]["count"] += 1
        buckets[key]["xg"] += xg
        buckets["total"]["xg"] += xg  # npxG accumulator

    return buckets

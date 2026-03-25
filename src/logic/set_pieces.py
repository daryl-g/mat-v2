# Logic for set piece analysis

# Imports
from utils import load_json, get_team_id

# ---------------------------------------------------------------------------
# Private helper functions and constants

# Opta qualifierIds
_CORNER_QUALIFIER: int = 6        # Marks a typeId=1 pass as a corner kick
_INSWING_QUALIFIER: int = 223     # Inswinging corner
_OUTSWING_QUALIFIER: int = 224    # Outswinging corner
_PASS_END_X_QUALIFIER: int = 140  # Pass delivery end x-coordinate
_PASS_END_Y_QUALIFIER: int = 141  # Pass delivery end y-coordinate

# Periods where the HOME team attacks in the opposite direction.
# Raw Opta coordinates are fixed-camera; we flip for these periods so that
# each team's corners always appear at x≈100 (their attacking end).
_HOME_SWAP_PERIODS: frozenset[int] = frozenset({2, 4})

# All sub-keys present in each team's corner dict.
_CORNER_KEYS: tuple[str, ...] = (
    "left_inswing",
    "left_outswing",
    "right_inswing",
    "right_outswing",
    "straight",
)


def _qualifier_map(event: dict) -> dict:
    """Return a flat {qualifierId: value} mapping for a single event."""
    return {q["qualifierId"]: q.get("value") for q in event.get("qualifier", [])}


def _normalize_xy(x: float, y: float, flip: bool) -> tuple[float, float]:
    """Flip (x, y) to the opposite end of the pitch when required."""
    return (100.0 - x, 100.0 - y) if flip else (x, y)


def _swing_label(inswing: bool, outswing: bool) -> str:
    if inswing:
        return "inswing"
    if outswing:
        return "outswing"
    return "straight"


def _corner_key(y: float, inswing: bool, outswing: bool) -> str:
    """Return the sub-key identifying a corner's side and swing type."""
    side = "left" if y >= 50.0 else "right"
    return f"{side}_{_swing_label(inswing, outswing)}"


def _extract_corner(event: dict) -> dict | None:
    """
    Return a dict of parsed corner fields, or None if the event is not a
    corner kick or lacks delivery end coordinates.
    """
    if event.get("typeId") != 1:
        return None
    qmap = _qualifier_map(event)
    if _CORNER_QUALIFIER not in qmap:
        return None
    ex = qmap.get(_PASS_END_X_QUALIFIER)
    ey = qmap.get(_PASS_END_Y_QUALIFIER)
    if ex is None or ey is None:
        return None
    return {
        "qmap": qmap,
        "raw_x": float(event.get("x", 0)),
        "raw_y": float(event.get("y", 0)),
        "raw_ex": float(ex),
        "raw_ey": float(ey),
    }

def _empty_buckets() -> dict:
    """Return an empty dict with a list pair for each corner sub-key."""
    return {k: {"x": [], "y": [], "end_x": [], "end_y": []} for k in _CORNER_KEYS}




def load_corners(event_path: str) -> dict:
    """
    Load corner kick delivery data for each team from an Opta events file.

    A corner is a typeId=1 pass that carries qualifierId 6.  Coordinates are
    normalised so that both teams always attack toward x=100:

    * Home team events in periods 2 & 4 are flipped (100-x, 100-y).
    * Away team events in periods 1 & 3 are flipped.

    After normalisation, corners are classified as ``left`` (y ≥ 50) or
    ``right`` (y < 50), and ``inswing`` (qualifier 223), ``outswing``
    (qualifier 224), or ``straight`` (neither).

    Args:
        event_path (str): Path to the Opta events JSON file.

    Returns:
        dict: Two keys, ``"home"`` and ``"away"``, each containing a dict
        keyed by corner type (``"left_inswing"``, ``"left_outswing"``,
        ``"right_inswing"``, ``"right_outswing"``, ``"straight"``).  Each
        value is a dict with ``"x"``, ``"y"``, ``"end_x"``, ``"end_y"``
        lists representing the kick origin and delivery end-point::

            {
                "home": {
                    "left_inswing":  {"x": [...], "y": [...], "end_x": [...], "end_y": [...]},
                    "right_inswing": {...},
                    ...
                },
                "away": {...},
            }
    """
    event_file = load_json(event_path)
    match_info = event_file.get("matchInfo", {})

    home_id = get_team_id(match_info, "home")
    away_id = get_team_id(match_info, "away")

    corners: dict = {
        "home": _empty_buckets(),
        "away": _empty_buckets(),
    }

    for event in event_file.get("liveData", {}).get("event", []):
        period = event.get("periodId", 0)
        if period not in (1, 2, 3, 4):
            continue
        parsed = _extract_corner(event)
        if parsed is None:
            continue

        contestant_id = event.get("contestantId")
        if contestant_id not in (home_id, away_id):
            continue

        is_home = contestant_id == home_id
        flip = (is_home and period in _HOME_SWAP_PERIODS) or (
            not is_home and period not in _HOME_SWAP_PERIODS
        )

        x, y = _normalize_xy(parsed["raw_x"], parsed["raw_y"], flip)
        nx, ny = _normalize_xy(parsed["raw_ex"], parsed["raw_ey"], flip)

        qmap = parsed["qmap"]
        key = _corner_key(y, _INSWING_QUALIFIER in qmap, _OUTSWING_QUALIFIER in qmap)
        side = "home" if is_home else "away"
        corners[side][key]["x"].append(x)
        corners[side][key]["y"].append(y)
        corners[side][key]["end_x"].append(nx)
        corners[side][key]["end_y"].append(ny)

    return corners

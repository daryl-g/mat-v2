# Logic to calculate team possession dominance and related stats

# Imports
from utils import load_json, get_team_id

# ---------------------------------------------------------------------------
# Private helper functions and constants

# Opta typeIds that represent a team being in possession of the ball.
# Excludes duels, tackles, clearances, and other non-possession contacts.
_TOUCH_TYPE_IDS: frozenset[int] = frozenset(
    {1, 2, 3, 7, 8, 12, 13, 14, 15, 16, 42, 44, 49, 50, 61, 73, 74}
)

# Periods where the home team attacks in the opposite direction (ends swap).
# Raw Opta coordinates are fixed-camera, so we rotate these 180° so that
# the home team always attacks left → right in the aggregate.
_SWAP_PERIODS: frozenset[int] = frozenset({2, 4})

# ---------------------------------------------------------------------------
# Public functions


def load_possession_versus(event_path: str) -> dict:
    """
    Load touch coordinates from an Opta events file, normalised so that the
    home team always attacks left → right across all periods.

    Only ball-in-possession events are included (passes, take-ons, shots).
    Duels, tackles, and clearances are excluded.

    Half-time ends-swap is corrected: events from ``periodId`` 2 (and 4 for
    extra time) are rotated 180° — ``x → 100 − x``, ``y → 100 − y`` — so
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

        # Rotate events from swap periods so the home team always attacks L→R
        if period_id in _SWAP_PERIODS:
            x = 100.0 - x
            y = 100.0 - y

        side = "home" if contestant_id == home_id else "away"
        touches[side]["x"].append(x)
        touches[side]["y"].append(y)

    return touches

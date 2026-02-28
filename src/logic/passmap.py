# Process and logic functions for the passmap file

# Imports
from utils import load_json, get_team_id


# ---------------------------------------------------------------------------
# Public functions


def load_pass_network(passmap_path: str, side: str = "home") -> dict:
    """
    Load the passing network data for the starting XI of the specified team.

    Only starters with valid average positions (x/y) are included. Passes
    between two players who are both in the starting XI are extracted.

    Args:
        passmap_path (str): Path to the Opta passmap JSON file.
        side (str): "home" or "away". Default is "home".

    Returns:
        dict: A dict with two keys:
            - ``players``: list of dicts, one per starter with x/y coords::

                {
                    "player_id":    str,
                    "name":         str,   # matchName
                    "shirt_no":     int,
                    "x":            float, # average x position (Opta coords)
                    "y":            float, # average y position (Opta coords)
                    "pass_success": int,   # number of accurate passes
                }

            - ``passes``: list of dicts for each passer→receiver combination::

                {
                    "from_id": str,  # playerId of the passer
                    "to_id":   str,  # playerId of the receiver
                    "value":   int,  # number of pass combinations
                }

        Only passes where both endpoints are in the starting XI are kept.
    """
    if side not in ("home", "away"):
        raise ValueError("side must be 'home' or 'away'")

    data = load_json(passmap_path)
    team_id = get_team_id(data.get("matchInfo", {}), side)

    lineup = data.get("liveData", {}).get("lineUp", [])
    team_lineup = next((t for t in lineup if t.get("contestantId") == team_id), None)
    if team_lineup is None:
        raise ValueError(f"No lineup found for side '{side}' in passmap file.")

    players = []
    raw_passes = []

    for player in team_lineup.get("player", []):
        # Starters always appear before substitutes; stop once we hit a sub
        if player.get("position") == "Substitute":
            break
        # Skip any starter missing positional data
        if "x" not in player or "y" not in player:
            continue

        players.append(
            {
                "player_id": player["playerId"],
                "name": player["matchName"],
                "shirt_no": player["shirtNumber"],
                "x": float(player["x"]),
                "y": float(player["y"]),
                "pass_success": int(player.get("passSuccess", 0)),
            }
        )

        for pp in player.get("playerPass", []):
            raw_passes.append(
                {
                    "from_id": player["playerId"],
                    "to_id": pp["playerId"],
                    "value": int(pp["value"]),
                }
            )

    # Only keep passes between two starters with positions
    starter_ids = {p["player_id"] for p in players}
    passes = [
        p
        for p in raw_passes
        if p["from_id"] in starter_ids and p["to_id"] in starter_ids
    ]

    return {"players": players, "passes": passes}

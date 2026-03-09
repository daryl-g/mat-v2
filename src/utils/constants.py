# Maps Opta stat types to display names. Formation is handled separately.
MATCH_STAT_TYPE_MAP = {
    "totalScoringAtt": "Shots attempted",
    "ontargetScoringAtt": "Shots on target",
    "possessionPercentage": "Possession %",
    "totalPass": "Passes made",
    "accuratePass": "Passes completed",
    "fkFoulLost": "Fouls committed",
    "totalYellowCard": "Yellow cards",
    "totalRedCard": "Red cards",
}
KEEPER_STAT_TYPE_MAP = {
    "minsPlayed": "Minutes played",
    "goalsConceded": "Goals conceded",
    "saves": "Saves",
    "totalPass": "Passes made",
    "accuratePass": "Passes completed",
    "goalKicks": "Goal kicks",
}
OUTFIELD_STAT_TYPE_MAP = {
    "position": "Position",
    "minsPlayed": "Minutes played",
    "goals": "Goals",
    "goalAssist": "Assists",
    "totalScoringAtt": "Shots attempted",
    "ontargetScoringAtt": "Shots on target",
    "totalPass": "Passes made",
    "accuratePass": "Passes completed",
    "totalTackle": "Tackles",
    "wonTackle": "Tackles won",
    "blockedScoringAtt": "Shots blocked",
    "totalClearance": "Clearances",
    "fouls": "Fouls committed",
    "yellowCard": "Yellow cards",
    "redCard": "Red cards",
}

# Maps period IDs to their summary key
PERIOD_ID_MAP = {1: "1H", 2: "2H", 3: "ET1", 4: "ET2"}

# Maps score keys in the data to summary keys
SCORE_KEY_MAP = {"ht": "ht", "ft": "ft", "et": "et", "pen": "penalties"}

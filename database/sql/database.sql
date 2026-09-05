# MAT database creation script - with PostgreSQL

# -----------------------------------------------------------
# Bronze schema
DROP SCHEMA IF EXISTS mat_bronze;
CREATE SCHEMA IF NOT EXISTS mat_bronze;

# Silver schema
DROP SCHEMA IF EXISTS mat_silver;
CREATE SCHEMA IF NOT EXISTS mat_silver;

# Gold schema
DROP SCHEMA IF EXISTS mat_gold;
CREATE SCHEMA IF NOT EXISTS mat_gold;

# -----------------------------------------------------------
# Bronze tables

# Raw Wikipedia data
DROP TABLE IF EXISTS mat_bronze.wiki_matches_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.wiki_matches_raw (
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now(),
    PRIMARY KEY (opta_competition_id, opta_calendar_id)
);

DROP TABLE IF EXISTS mat_bronze.wiki_teams_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.wiki_teams_raw (
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now(),
    PRIMARY KEY (opta_competition_id, opta_calendar_id)
);

DROP TABLE IF EXISTS mat_bronze.wiki_squads_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.wiki_squads_raw (
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now(),
    PRIMARY KEY (opta_competition_id, opta_calendar_id)
);

DROP TABLE IF EXISTS mat_bronze.wiki_standings_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.wiki_standings_raw (
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now(),
    PRIMARY KEY (opta_competition_id, opta_calendar_id)
);

DROP TABLE IF EXISTS mat_bronze.wiki_groups_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.wiki_groups_raw (
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now(),
    PRIMARY KEY (opta_competition_id, opta_calendar_id)
);

DROP TABLE IF EXISTS mat_bronze.wiki_stages_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.wiki_stages_raw (
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now(),
    PRIMARY KEY (opta_competition_id, opta_calendar_id)
);

# Raw Opta data
DROP TABLE IF EXISTS mat_bronze.opta_events_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.opta_events_raw (
    opta_match_id varchar(25) PRIMARY KEY DEFAULT '',
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS mat_bronze.opta_stats_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.opta_stats_raw (
    opta_match_id varchar(25) PRIMARY KEY DEFAULT '',
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS mat_bronze.opta_passmaps_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.opta_passmaps_raw (
    opta_match_id varchar(25) PRIMARY KEY DEFAULT '',
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now()
);

DROP TABLE IF EXISTS mat_bronze.opta_xgoals_raw;
CREATE TABLE IF NOT EXISTS mat_bronze.opta_xgoals_raw (
    opta_match_id varchar(25) PRIMARY KEY DEFAULT '',
    opta_competition_id varchar(25) NOT NULL DEFAULT '',
    opta_calendar_id varchar(25) NOT NULL DEFAULT '',
    content jsonb NOT NULL DEFAULT '{}',
    added timestampz NOT NULL DEFAULT now()
);

# -----------------------------------------------------------
# Silver tables

DROP TABLE IF EXISTS mat_silver.competition;
CREATE TABLE IF NOT EXISTS mat_silver.competition (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    name text NOT NULL DEFAULT '',
    known_name text NOT NULL DEFAULT '',
    tournament_calendar_id uuid NOT NULL DEFAULT uuidv7(),
    tournament_calendar text NOT NULL DEFAULT '',
    start_date date NOT NULL,
    end_date date NOT NULL,
);

DROP TABLE IF EXISTS mat_silver.stage;
CREATE TABLE IF NOT EXISTS mat_silver.stage (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    competition_id uuid NOT NULL REFERENCES competition(id) ON DELETE CASCADE ON UPDATE CASCADE,
    tournament_calendar_id uuid NOT NULL REFERENCES competition(tournament_calendar_id) ON DELETE CASCADE ON UPDATE CASCADE
    name varchar(255) NOT NULL DEFAULT '',
    start_date date NOT NULL,
    end_date date NOT NULL
    /*
        When a parent competition ID/tournament calendar ID is deleted, its child stage(s) will also be deleted.
        When a parent competition ID/tournament calendar ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.series;
CREATE TABLE IF NOT EXISTS mat_silver.series (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    stage_id uuid NOT NULL REFERENCES stage(id) ON DELETE CASCADE ON UPDATE CASCADE,
    name varchar(255) NOT NULL DEFAULT '',
    order smallint NOT NULL DEFAULT 1
    /*
        When a parent stage ID is deleted, its child series will also be deleted.
        When a parent stage ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.country;
CREATE TABLE IF NOT EXISTS mat_silver.country (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    name varchar(255) NOT NULL DEFAULT '',
    code varchar(3) NOT NULL DEFAULT ''
);

DROP TABLE IF EXISTS mat_silver.team;
CREATE TABLE IF NOT EXISTS mat_silver.team (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    name text NOT NULL DEFAULT '',
    short_name text NOT NULL DEFAULT '',
    official_name text NOT NULL DEFAULT '',
    code varchar(3) NOT NULL DEFAULT '',
    country_id uuid DEFAULT NULL REFERENCES country(id) ON DELETE SET NULL ON UPDATE CASCADE
    /*
        When a parent country ID is deleted, its child team will be detached and set null.
        When a parent country ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.contestant;
CREATE TABLE IF NOT EXISTS mat_silver.contestant (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    team_id uuid NOT NULL REFERENCES team(id) ON DELETE CASCADE ON UPDATE CASCADE,
    competition_id uuid NOT NULL REFERENCES competition(id) ON DELETE CASCADE ON UPDATE CASCADE,
    tournament_calendar_id uuid NOT NULL REFERENCES competition(tournament_calendar_id) ON DELETE CASCADE ON UPDATE CASCADE
    /*
        When a parent team/competition/tournament calendar ID is deleted, its child contestant(s) will also be deleted.
        When a parent team/competition/tournament calendar ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.match_info;
CREATE TABLE IF NOT EXISTS mat_silver.match_info (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    description text NOT NULL DEFAULT '',
    local_date date NOT NULL,
    local_time timestamptz NOT NULL,
    last_updated timestamptz NOT NULL,
    competition_id uuid REFERENCES competition(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    tournament_calendar_id uuid REFERENCES competition(tournament_calendar_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    stage_id uuid REFERENCES stage(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    series_id uuid REFERENCES series(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    home_team_id uuid REFERENCES contestant(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    away_team_id uuid REFERENCES contestant(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    venue_neutral boolean NOT NULL DEFAULT FALSE,
    venue_short_name text NOT NULL DEFAULT '',
    venue_long_name text NOT NULL DEFAULT ''
    /*
        When a parent ID is deleted, the deletion will not proceed due to restrictions on foreign keys.
        When a parent ID is updated, the update will also affect the child IDs.
    */
);

DROP TABLE IF EXISTS mat_silver.player;
CREATE TABLE IF NOT EXISTS mat_silver.player (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    first_name text NOT NULL DEFAULT '',
    last_name text NOT NULL DEFAULT '',
    short_first_name text NOT NULL DEFAULT '',
    short_last_name text NOT NULL DEFAULT '',
    known_name text NOT NULL DEFAULT '',
    match_name text NOT NULL DEFAULT '',
    date_of_birth date NOT NULL,
    club_id uuid REFERENCES team(id) ON DELETE SET NULL ON UPDATE CASCADE,
    national_team_id uuid REFERENCES team(id) ON DELETE SET NULL ON UPDATE CASCADE,
    nationality_id uuid REFERENCES country(id) ON DELETE SET NULL ON UPDATE CASCADE,
    main_position string DEFAULT ''
    /*
        When a parent ID is deleted, the child IDs will be set to NULL.
        When a parent ID is updated, the update will also affect the child IDs.
    */
);

DROP TABLE IF EXISTS mat_silver.lineup;
CREATE TABLE IF NOT EXISTS mat_silver.lineup (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    team_id uuid REFERENCES team(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    match_id uuid REFERENCES match_info(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    player_id uuid REFERENCES player(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    shirt_number smallint NOT NULL DEFAULT 0,
    played_position varchar(50) NOT NULL DEFAULT '',
    position_side varchar(50) NOT NULL DEFAULT ''
    /*
        When a parent ID is deleted, the deletion will not proceed due to restrictions on foreign keys.
        When a parent ID is updated, the update will also affect the child IDs.
    */
);

DROP TABLE IF EXISTS mat_silver.match_event;
CREATE TABLE IF NOT EXISTS mat_silver.match_event (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    match_id uuid REFERENCES match_info(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    event_id integer NOT NULL DEFAULT 1,
    type_id integer NOT NULL DEFAULT 1,
    time_min integer NOT NULL DEFAULT 0,
    time_sec integer NOT NULL DEFAULT 0,
    team_id uuid REFERENCES team(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    player_id uuid REFERENCES lineup(player_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    outcome integer NOT NULL DEFAULT 0,
    x real NOT NULL DEFAULT 0.0,
    y real NOT NULL DEFAULT 0.0,
    event_timestamp timestampz NOT NULL,
    last_modified timestampz NOT NULL
    /*
        When a parent ID is deleted, the deletion will not proceed due to restrictions on foreign keys.
        When a parent ID is updated, the update will also affect the child IDs.
    */
);

DROP TABLE IF EXISTS mat_silver.event_qualifier;
CREATE TABLE IF NOT EXISTS mat_silver.event_qualifier (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    event_id uuid REFERENCES match_event(id) ON DELETE CASCADE ON UPDATE CASCADE,
    qualifier_id integer NOT NULL DEFAULT 1,
    value TEXT NOT NULL DEFAULT ''
    /*
        When a parent event ID is deleted, its child qualifier(s) will also be deleted.
        When a parent event ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.match_details;
CREATE TABLE IF NOT EXISTS mat_silver.match_details (
    match_id uuid PRIMARY KEY REFERENCES match_event(id) ON DELETE CASCADE ON UPDATE CASCADE,
    match_played boolean NOT NULL DEFAULT FALSE,
    match_status string NOT NULL DEFAULT '',
    match_winner uuid REFERENCES contestant(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    match_length_min smallint NOT NULL DEFAULT 0,
    match_length_sec smallint NOT NULL DEFAULT 0
    /*
        When a parent event ID is deleted, its child qualifier(s) will also be deleted.
        When a parent event ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.match_period;
CREATE TABLE IF NOT EXISTS mat_silver.match_period (
    match_id uuid PRIMARY KEY REFERENCES match_event(id) ON DELETE CASCADE ON UPDATE CASCADE,
    period_id smallint NOT NULL DEFAULT 1,
    length_min smallint NOT NULL DEFAULT 0,
    length_sec smallint NOT NULL DEFAULT 0,
    total_injury_time smallint NOT NULL DEFAULT 0
    /*
        When a parent event ID is deleted, its child qualifier(s) will also be deleted.
        When a parent event ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.match_score;
CREATE TABLE IF NOT EXISTS mat_silver.match_score (
    match_id uuid PRIMARY KEY REFERENCES match_event(id) ON DELETE CASCADE ON UPDATE CASCADE,
    period_id smallint NOT NULL DEFAULT 1,
    milestone varchar(255) NOT NULL DEFAULT '',
    home_score smallint NOT NULL DEFAULT 0,
    away_score smallint NOT NULL DEFAULT 0
    /*
        When a parent event ID is deleted, its child qualifier(s) will also be deleted.
        When a parent event ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.passmap;
CREATE TABLE IF NOT EXISTS mat_silver.passmap (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    match_id uuid NOT NULL REFERENCES match_event(id) ON DELETE CASCADE ON UPDATE CASCADE,
    passer_id uuid NOT NULL REFERENCES lineup(player_id) ON DELETE CASCADE ON UPDATE CASCADE,
    receiver_id uuid NOT NULL REFERENCES lineup(player_id) ON DELETE CASCADE ON UPDATE CASCADE,
    value smallint NOT NULL DEFAULT 0
    /*
        When a parent event ID is deleted, its child qualifier(s) will also be deleted.
        When a parent event ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.team_stats;
CREATE TABLE IF NOT EXISTS mat_silver.team_stats (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    match_id uuid NOT NULL REFERENCES match_event(id) ON DELETE CASCADE ON UPDATE CASCADE,
    team_id uuid NOT NULL REFERENCES contestant(id) ON DELETE CASCADE ON UPDATE CASCADE
    /*
        When a parent event ID is deleted, its child qualifier(s) will also be deleted.
        When a parent event ID is updated, the update will also change the IDs of the child.
    */
);

DROP TABLE IF EXISTS mat_silver.team_stats;
CREATE TABLE IF NOT EXISTS mat_silver.team_stats (
    id uuid PRIMARY KEY DEFAULT uuidv7(),
    match_id uuid NOT NULL REFERENCES match_event(id) ON DELETE CASCADE ON UPDATE CASCADE,
    player_id uuid NOT NULL REFERENCES lineup(player_id) ON DELETE CASCADE ON UPDATE CASCADE,
    average_x real NOT NULL DEFAULT 0.0,
    average_y real NOT NULL DEFAULT 0.0
    /*
        When a parent event ID is deleted, its child qualifier(s) will also be deleted.
        When a parent event ID is updated, the update will also change the IDs of the child.
    */
);

# -----------------------------------------------------------
# Gold materialised views
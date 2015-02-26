-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


CREATE TABLE players (name TEXT,
					id SERIAL primary key );

CREATE TABLE matches (winner SMALLINT references players(id),
                    loser SMALLINT references players(id),
                    match_id SERIAL primary key );

CREATE VIEW matches_w_names AS (
	SELECT match_id, winner, name as loser
	FROM (
		SELECT match_id, name as winner, loser 
		FROM matches 
		RIGHT JOIN players
		ON winner = id
	) temp
	JOIN players on id = loser
);

CREATE VIEW total_matches_table AS (
	SELECT name, count(name) as total_matches
	FROM (
		SELECT winner as name 
		FROM matches_w_names
		UNION ALL
		SELECT loser
		FROM matches_w_names
	) tmp
	GROUP BY name
);

CREATE VIEW total_wins_table AS (
	SELECT winner, count(winner) as total_wins
	FROM matches_w_names
	GROUP BY winner
);

CREATE VIEW total_wins_and_matches_table AS (
	SELECT name,
	CASE WHEN tw.total_wins >= 0 
            THEN tw.total_wins 
            ELSE 0
    END as total_wins, total_matches
	FROM total_matches_table tm
	LEFT JOIN total_wins_table tw 
	ON tw.winner = tm.name
);

CREATE VIEW playerStandings AS (
	SELECT players.id, 
		players.name,
		CASE WHEN total_wins >= 0
			THEN total_wins
			ELSE 0
		END AS total_wins, 
		CASE WHEN total_matches >= 0
			THEN total_matches
			ELSE 0
		END AS total_matches
	FROM total_wins_and_matches_table tw
	RIGHT JOIN players
	ON players.name=tw.name
	ORDER BY total_wins desc
);
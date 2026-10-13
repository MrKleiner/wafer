-- PRAGMA foreign_keys = ON;
-- PRAGMA journal_mode = WAL;
-- PRAGMA synchronous =  NORMAL;
-- PRAGMA busy_timeout = 5000;



CREATE TABLE IF NOT EXISTS kv_params (
	p_k TEXT    NOT NULL UNIQUE,
	p_v TEXT,
	p_t INTEGER NOT NULL
);



-- Needed to make it impossible for clients (human or not)
-- to engage in edging with the server.
CREATE TABLE IF NOT EXISTS journal (
	-- Which chunk this upload journal record is for
	chunk_index INTEGER NOT NULL,
	-- Whether upload went fine
	okay_mate   BOOLEAN NOT NULL,
	-- When this journal record was inserted
	tstamp      INTEGER NOT NULL,
	-- Optional detailed description of what this record means
	descr       TEXT
);



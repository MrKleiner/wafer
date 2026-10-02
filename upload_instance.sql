-- PRAGMA foreign_keys = ON;
-- PRAGMA journal_mode = WAL;
-- PRAGMA synchronous =  NORMAL;
-- PRAGMA busy_timeout = 5000;


CREATE TABLE IF NOT EXISTS kv_params (
	p_k TEXT    NOT NULL UNIQUE,
	p_v TEXT,
	p_t INTEGER NOT NULL
);



CREATE TABLE IF NOT EXISTS journal (
	chunk_index INTEGER NOT NULL,
	okay_mate   BOOLEAN NOT NULL,
	tstamp      INTEGER NOT NULL,
	descr       TEXT
);



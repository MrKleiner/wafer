-- PRAGMA foreign_keys = ON;
-- PRAGMA journal_mode = WAL;
-- PRAGMA synchronous =  NORMAL;
-- PRAGMA busy_timeout = 5000;



CREATE TABLE IF NOT EXISTS profiles (
	-- 5360bfc5-ad70-4314-8f2c-84330c02be1a
	userid         TEXT NOT NULL UNIQUE PRIMARY KEY,

	-- admin
	login          TEXT NOT NULL UNIQUE,
	-- 1
	pswd           TEXT NOT NULL,

	-- Paused accounts can't do shit.
	-- Not even login into the system.
	-- As if this account doesn't even exist...
	paused         BOOLEAN NOT NULL DEFAULT 0,

	-- WOULD YOU BELIEVE THAT I'VE ALREADY REACHED THAT CONCLUSION ?!
	sugmar         BOOLEAN NOT NULL DEFAULT 0,

	-- User creation date as unix timestamp.
	-- Automated, optional
	created_tstamp INTEGER,

	-- Fuck you all
	failed_auth_attempts INTEGER NOT NULL DEFAULT 0,

	-- Short description, optional
	descr TEXT
);



CREATE TABLE IF NOT EXISTS tokens (
	userid         TEXT    NOT NULL,

	-- d31a091f854bb063ca0cf817eba33414a9503fb96ac000313bbe8118fbac95ae
	token_data     TEXT    NOT NULL UNIQUE,

	-- Unix timestamps
	created_tstamp INTEGER NOT NULL,
	expires_tstamp INTEGER NOT NULL,

	FOREIGN KEY (userid)
		REFERENCES profiles(userid)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);



-- EVERYBODY IS CRAZY EXCEPT ME
CREATE TABLE IF NOT EXISTS ip_table (
	userid  TEXT NOT NULL,

	ip      TEXT NOT NULL,
	tstamp  INTEGER,

	-- 0 = login ok
	-- 1 = login fail
	reason  INTEGER,

	FOREIGN KEY (userid)
		REFERENCES profiles(userid)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);



-- This table is needed to tie uploads to users,
-- so that they can resume them
CREATE TABLE IF NOT EXISTS uploads (
	userid    TEXT NOT NULL,

	-- 5360bfc5-ad70-4314-8f2c-84330c02be1a
	upload_id TEXT NOT NULL UNIQUE,

	-- 0 = okay mate
	-- 1 = pending
	-- 2 = expired (the client took far too long to finish uploading)
	-- 3 = max retry amount exceeded
	-- 4 = upload done, but in the time it took the upload to finish - 
	--     something has changed and now the "desired_relpath" is invalid or some shit...
	--     (Basically, fatal failure of writing uploaded data to the desired filepath)
	-- 5 = the client forcefully refused continuing this upload
	-- 6 = irreversible fatal server error
	status    INTEGER NOT NULL,

	-- Desired upload path, relative to root
	-- /fuck/shit/pootis.mp4
	desired_relpath TEXT,

	-- At what point this upload ended forever, irreversibly.
	-- Very tied to "status".
	-- Needed so that the journal can be purged of dead uploads
	-- older than specified amount of time.
	postmortem_tstamp INTEGER,

	FOREIGN KEY (userid)
		REFERENCES profiles(userid)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);



CREATE TABLE IF NOT EXISTS masks (
	mask_id INTEGER PRIMARY KEY AUTOINCREMENT,

	-- /fuck/shit/**
	-- /pootis/medic/dispenser.*
	-- /piss/*/off
	text_lines   TEXT    NOT NULL DEFAULT "",

	-- 0 = no action
	-- 1 = force allow
	-- 2 = force prohibit
	perm_view    INTEGER NOT NULL DEFAULT 0,
	perm_mkfile  INTEGER NOT NULL DEFAULT 0,
	perm_mkdir   INTEGER NOT NULL DEFAULT 0,

	-- 0 = wcmatch
	-- 1 = fnmatch
	syntax       INTEGER NOT NULL DEFAULT 0,

	-- Short optional description
	descr        TEXT

	-- CHECK (perm_view   BETWEEN 0 AND 2),
	-- CHECK (perm_mkfile BETWEEN 0 AND 2),
	-- CHECK (perm_mkdir  BETWEEN 0 AND 2)
);



CREATE TABLE IF NOT EXISTS mask_linkage (
	mask_id INTEGER NOT NULL,
	userid  TEXT    NOT NULL,

	-- This mask's order in the target user's mask stack.
	-- Higher values "override" lower values.
	idx     INTEGER NOT NULL,

	-- Because horrible fucking shit can happen
	-- if the "default" /** gets placed somewhere it shouldn't be.
	UNIQUE (userid, idx),

	FOREIGN KEY (mask_id)
		REFERENCES masks(mask_id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
	,

	FOREIGN KEY (userid)
		REFERENCES profiles(userid)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);










CREATE INDEX IF NOT EXISTS idx_ip_table
	ON ip_table(userid);

CREATE INDEX IF NOT EXISTS idx_tokens_userid
	ON tokens(userid);

CREATE INDEX IF NOT EXISTS idx_uploads_userid
	ON uploads(userid);

CREATE INDEX IF NOT EXISTS idx_mask_linkage_userid
	ON mask_linkage(userid);

CREATE INDEX IF NOT EXISTS idx_mask_linkage_mask_id
	ON mask_linkage(mask_id);




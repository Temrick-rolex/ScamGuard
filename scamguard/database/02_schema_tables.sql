-- ScamGuard - schema PostgreSQL 18 genere depuis les modeles SQLAlchemy
-- Genere par : PYTHONPATH=. python scripts/export_schema.py
-- Ne pas modifier a la main : modifiez app/models/ puis regenerez.

\connect scamguard

CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE dw_dim_date (
	date_key SERIAL NOT NULL, 
	day DATE NOT NULL, 
	week INTEGER NOT NULL, 
	month INTEGER NOT NULL, 
	year INTEGER NOT NULL, 
	PRIMARY KEY (date_key), 
	UNIQUE (day)
);

CREATE TABLE dw_dim_label (
	label_key SERIAL NOT NULL, 
	label_name VARCHAR(20) NOT NULL, 
	PRIMARY KEY (label_key), 
	UNIQUE (label_name)
);

CREATE TABLE dw_dim_source (
	source_key SERIAL NOT NULL, 
	source_name VARCHAR(60) NOT NULL, 
	source_type VARCHAR(30) NOT NULL, 
	reliability INTEGER NOT NULL, 
	PRIMARY KEY (source_key), 
	UNIQUE (source_name)
);

CREATE TABLE dw_dim_type (
	type_key SERIAL NOT NULL, 
	type_name VARCHAR(20) NOT NULL, 
	PRIMARY KEY (type_key), 
	UNIQUE (type_name)
);

CREATE TABLE dw_etl_runs (
	run_id SERIAL NOT NULL, 
	script_version VARCHAR(20) NOT NULL, 
	started_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	ended_at TIMESTAMP WITH TIME ZONE, 
	rows_extracted INTEGER NOT NULL, 
	rows_loaded INTEGER NOT NULL, 
	rows_rejected INTEGER NOT NULL, 
	notes VARCHAR(500) NOT NULL, 
	PRIMARY KEY (run_id)
);

CREATE TABLE login_attempts (
	id SERIAL NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	ip VARCHAR(45) NOT NULL, 
	successful BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_login_attempts_created_at ON login_attempts (created_at);
CREATE INDEX ix_login_attempts_email ON login_attempts (email);

CREATE TABLE phone_reputation (
	phone VARCHAR(20) NOT NULL, 
	report_count INTEGER NOT NULL, 
	confirmed_count INTEGER NOT NULL, 
	score INTEGER NOT NULL, 
	main_reason VARCHAR(120) NOT NULL, 
	last_reported_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (phone)
);

CREATE TABLE report_groups (
	id SERIAL NOT NULL, 
	content_hash VARCHAR(64) NOT NULL, 
	content_redacted TEXT NOT NULL, 
	main_reason VARCHAR(30) NOT NULL, 
	suspect_phone VARCHAR(20), 
	report_count INTEGER NOT NULL, 
	validated_count INTEGER NOT NULL, 
	published BOOLEAN NOT NULL, 
	first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_report_groups_suspect_phone ON report_groups (suspect_phone);
CREATE UNIQUE INDEX ix_report_groups_content_hash ON report_groups (content_hash);
CREATE INDEX ix_report_groups_last_seen_at ON report_groups (last_seen_at);
CREATE INDEX ix_report_groups_published ON report_groups (published);

CREATE TABLE url_reputation_cache (
	url_hash VARCHAR(64) NOT NULL, 
	verdict VARCHAR(20) NOT NULL, 
	score INTEGER NOT NULL, 
	source VARCHAR(30) NOT NULL, 
	fetched_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (url_hash)
);

CREATE TABLE users (
	id SERIAL NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	phone VARCHAR(20), 
	full_name VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role role NOT NULL, 
	status accountstatus NOT NULL, 
	is_premium BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE UNIQUE INDEX ix_users_phone ON users (phone);

CREATE TABLE analyses (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	analysis_type VARCHAR(10) NOT NULL, 
	input_redacted TEXT NOT NULL, 
	input_hash VARCHAR(64) NOT NULL, 
	risk_score INTEGER NOT NULL, 
	risk_level VARCHAR(12) NOT NULL, 
	confidence VARCHAR(12) NOT NULL, 
	explanations TEXT NOT NULL, 
	model_version VARCHAR(20) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_analyses_user_id ON analyses (user_id);
CREATE INDEX ix_analyses_risk_level ON analyses (risk_level);
CREATE INDEX ix_analyses_input_hash ON analyses (input_hash);
CREATE INDEX ix_analyses_created_at ON analyses (created_at);

CREATE TABLE audit_logs (
	id SERIAL NOT NULL, 
	actor_id INTEGER, 
	action VARCHAR(80) NOT NULL, 
	target_type VARCHAR(40) NOT NULL, 
	target_id VARCHAR(40) NOT NULL, 
	detail VARCHAR(500) NOT NULL, 
	ip VARCHAR(45) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(actor_id) REFERENCES users (id)
);

CREATE INDEX ix_audit_logs_actor_id ON audit_logs (actor_id);
CREATE INDEX ix_audit_logs_created_at ON audit_logs (created_at);
CREATE INDEX ix_audit_logs_action ON audit_logs (action);

CREATE TABLE device_settings (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	sms_protection BOOLEAN NOT NULL, 
	call_alert BOOLEAN NOT NULL, 
	notifications BOOLEAN NOT NULL, 
	last_sync_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE dw_fact_content (
	content_key SERIAL NOT NULL, 
	content_hash VARCHAR(64) NOT NULL, 
	content_anonymise TEXT NOT NULL, 
	source_key INTEGER NOT NULL, 
	label_key INTEGER NOT NULL, 
	type_key INTEGER NOT NULL, 
	date_key INTEGER NOT NULL, 
	run_id INTEGER NOT NULL, 
	langue VARCHAR(10) NOT NULL, 
	longueur INTEGER NOT NULL, 
	nb_liens INTEGER NOT NULL, 
	nb_numeros INTEGER NOT NULL, 
	PRIMARY KEY (content_key), 
	CONSTRAINT uq_fact_content_hash UNIQUE (content_hash), 
	FOREIGN KEY(source_key) REFERENCES dw_dim_source (source_key), 
	FOREIGN KEY(label_key) REFERENCES dw_dim_label (label_key), 
	FOREIGN KEY(type_key) REFERENCES dw_dim_type (type_key), 
	FOREIGN KEY(date_key) REFERENCES dw_dim_date (date_key), 
	FOREIGN KEY(run_id) REFERENCES dw_etl_runs (run_id)
);

CREATE INDEX ix_dw_fact_content_content_hash ON dw_fact_content (content_hash);

CREATE TABLE refresh_tokens (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	revoked_at TIMESTAMP WITH TIME ZONE, 
	replaced_by VARCHAR(64), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX ix_refresh_tokens_token_hash ON refresh_tokens (token_hash);
CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens (user_id);

CREATE TABLE reports (
	id SERIAL NOT NULL, 
	reporter_id INTEGER NOT NULL, 
	content_redacted TEXT NOT NULL, 
	content_hash VARCHAR(64) NOT NULL, 
	reason VARCHAR(30) NOT NULL, 
	comment VARCHAR(500) NOT NULL, 
	evidence_kind VARCHAR(20) NOT NULL, 
	suspect_phone VARCHAR(20), 
	suspect_url VARCHAR(500), 
	risk_score INTEGER NOT NULL, 
	risk_level VARCHAR(12) NOT NULL, 
	status VARCHAR(12) NOT NULL, 
	moderator_id INTEGER, 
	moderation_note VARCHAR(300) NOT NULL, 
	moderated_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(reporter_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(moderator_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_reports_created_at ON reports (created_at);
CREATE INDEX ix_reports_status ON reports (status);
CREATE INDEX ix_reports_suspect_phone ON reports (suspect_phone);
CREATE INDEX ix_reports_content_hash ON reports (content_hash);
CREATE INDEX ix_reports_reporter_id ON reports (reporter_id);

-- Reset in reverse order
drop table if exists sweepstakes.point_system;
drop table if exists sweepstakes.espn_round_data;
drop table if exists sweepstakes.sweepstake_picks;
drop table if exists sweepstakes.espn_player_pool;
drop table if exists sweepstakes.espn_events;
drop table if exists events.event_results;
drop table if exists events.competitors;
drop table if exists events.events;
drop table if exists events.event_types;
drop table if exists events.courses;
drop table if exists events.tournaments;
drop table if exists events.series;
drop table if exists core.users;
drop table if exists core.membership;

-- Core

create table core.membership (
	member_type_id serial primary key,
	member_type varchar(50) unique not null
);

create table core.users (
	user_id uuid unique not null primary key,
	user_name varchar(50) not null,
	user_email varchar(100) unique not null,
	user_auth_method char(1) not null,
	user_password varchar(100),
	user_role varchar(25) not null,
	member_type_id int not null references core.membership(member_type_id),
	user_member_verified boolean not null
);

-- Events

create table events.series (
	series_id uuid unique not null primary key,
	series_name varchar(50) not null,
	series_year int not null
);

create table events.tournaments (
	tournament_id uuid unique not null primary key,
	series_id uuid not null references events.series(series_id),
	tournament_name varchar(50) not null,
	tournament_start_date date not null,
	tournament_end_date date not null,
	check (tournament_end_date >= tournament_start_date)
);

create table events.courses (
	course_id uuid unique not null primary key,
	golfcourseapi_course_id int not null,
	club_name varchar(100) not null,
	course_name varchar(100) not null,
	course_location varchar(300) not null,
	course_holes int not null,
	course_par int not null,
	golfcourseapi_tee_data text not null
);

create table events.event_types (
	event_type_id serial primary key,
	event_type varchar(50) not null
);

insert into events.event_types (event_type) values('Stableford'),('Stroke'),('Match'),('Sweepstakes'),('Scramble');

create table events.events (
	event_id uuid unique not null primary key,
	event_type_id int not null references events.event_types(event_type_id),
	tournament_id uuid not null references events.tournaments(tournament_id),
	event_name varchar(100) not null,
	course_id uuid references events.courses(course_id),
	check (course_id <> null or event_type_id <> 4)
);

create table events.competitors (
	competitor_id uuid unique not null primary key,
	event_id uuid not null references events.events(event_id),
	user_id uuid not null references core.users(user_id),
	event_signed_up boolean not null default TRUE,
	event_deposit boolean not null default TRUE,
	event_paid boolean not null default TRUE
);

create table events.event_results (
	event_result_id uuid unique not null primary key,
	event_id uuid not null references events.events(event_id),
	competitor_id uuid not null references events.competitors(competitor_id),
	event_scorecard text
);

-- Sweepstakes

create table sweepstakes.espn_events (
	espn_event_id int unique not null primary key,
	event_id uuid unique not null references events.events(event_id),
	event_name varchar(100) not null,
	event_series varchar(50) not null
);

create table sweepstakes.espn_player_pool (
	espn_player_pool_id uuid unique not null primary key,
	espn_event_id int not null,
	espn_player_id int not null,
	espn_player_name varchar(100) not null
);

create table sweepstakes.sweepstake_picks (
	sweepstake_pick_id uuid unique not null primary key,
	competitor_id uuid not null references events.competitors(competitor_id),
	pick_1_id uuid not null references sweepstakes.espn_player_pool(espn_player_pool_id),
	pick_2_id uuid not null references sweepstakes.espn_player_pool(espn_player_pool_id),
	pick_3_id uuid not null references sweepstakes.espn_player_pool(espn_player_pool_id),
	pick_4_id uuid not null references sweepstakes.espn_player_pool(espn_player_pool_id),
	pick_5_id uuid not null references sweepstakes.espn_player_pool(espn_player_pool_id),
	pick_datetime timestamp not null,
	latest boolean not null	
);

create table sweepstakes.espn_round_data (
	round_data_id uuid unique not null primary key,
	espn_event_id int not null references sweepstakes.espn_events(espn_event_id),
	espn_player_pool_id uuid not null references sweepstakes.espn_player_pool(espn_player_pool_id),
	round_id int not null,
	espn_result_data text,
	parse_hio int not null,
	parse_albatross int not null,
	parse_eagle int not null,
	parse_birdie int not null,
	parse_par int not null,
	parse_bogey int not null,
	parse_dbogey int not null,
	parse_wbogey int not null,
	bogey_free boolean not null,
	eor_pos int not null,
	made_cut boolean,
	points int not null
);

create table sweepstakes.point_system (
	event_id uuid not null primary key references events.events(event_id),
	points_per_hio int default 10,
	points_per_albatross int default 0,
	points_per_eagle int default 0,
	points_per_birdie int default 0,
	points_per_par int default 0,
	points_per_bogey int default 0,
	points_per_dbogey int default 0,
	points_per_wbogey int default 0,
	points_if_bogey_free int default 2,
	points_if_made_cut int default 5
);
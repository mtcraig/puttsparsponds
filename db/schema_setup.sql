-- Core
drop table if exists core.users;
drop table if exists core.membership;

create table core.membership (
	member_type_id serial primary key,
	member_type varchar(50) unique not null
);

create table core.users (
	user_id serial primary key,
	user_name varchar(50) not null,
	user_email varchar(100) unique not null,
	user_auth_method char(1) not null,
	user_password varchar(100),
	user_role varchar(25) not null,
	member_type_id int not null references core.membership(member_type_id),
	user_member_verified boolean not null
);

-- Events
drop table if exists events.event_results
drop table if exists events.courses;
drop table if exists events.event_types;
drop table if exists events.competitors;
drop table if exists events.events;
drop table if exists events.tournaments;
drop table if exists events.series;

create table events.series (
	series_id serial primary key,
	series_name varchar(50) not null,
	series_year int not null
);

create table events.tournaments (
	tournament_id serial primary key,
	series_id int not null references events.series(series_id),
	tournament_name varchar(50) not null,
	tournament_start_date date not null,
	tournament_end_date date not null,
	check (tournament_end_date > tournament_start_date)
);

create table events.courses (
	course_id serial primary key,
	golfcourseapi_course_id int not null,
	club_name varchar(100) not null,
	course_name varchar(100) not null,
	course_location varchar(200) not null,
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
	event_id serial primary key,
	event_type_id int not null references events.event_types(event_type_id),
	tournament_id int not null references events.tournaments(tournament_id),
	event_name varchar(100) not null,
	course_id int references events.courses(course_id),
	check (course_id <> null or event_type_id <> 4)
);

create table events.competitors (
	competitor_id serial primary key,
	event_id int not null references events.events(event_id),
	user_id int not null references core.users(user_id),
	event_signed_up boolean not null default=TRUE,
	event_deposit boolean not null default=TRUE,
	event_paid boolean not null default=TRUE
);

create table events.event_results (
	event_result_id serial primary key,
	event_id int not null references events.events(event_id)
	competitor_id not null references events.competitors(competitor_id),
	event_scorecard text
);

-- Sweepstakes

create table sweepstakes.espn_events (
	espn_event_id not null primary key,
	event_name varchar(100) not null,
	event_series varchar(50) not null
);

create table sweepstakes.espn_player_pool (
	espn_player_id not null primary key,
	player_name varchar(100) not null
);

create table sweepstakes.sweepstake_picks (
	sweepstake_pick_id serial primary key,
	event_id int not null references events.events(event_id),
	competitor_id int not null references events.competitors(competitor_id),
	pick_1_id not null references espn.player_pool(player_id),
	pick_2_id not null references espn.player_pool(player_id),
	pick_3_id not null references espn.player_pool(player_id),
	pick_4_id not null references espn.player_pool(player_id),
	pick_5_id not null references espn.player_pool(player_id)
);

create table sweepstakes.espn_round_data (
	espn_event_id int not null references sweepstakes.espn_events(espn_event_id),
	espn_player_id int not null references sweepstakes.espn_player_pool(espn_player_id),
	round_id float not null, -- 2 / 2.5 / 3 for handling the cut
	espn_h1,
	espn_h2,
	espn_h3,
	espn_h4,
	espn_h5,
	espn_h6,
	espn_h7,
	espn_h8,
	espn_h9,
	espn_h10,
	espn_h11,
	espn_h12,
	espn_h13,
	espn_h14,
	espn_h15,
	espn_h16,
	espn_h17,
	espn_h18,
	parse_hio int not null,
	parse_albatross int not null,
	parse_eagle int not null,
	parse_birdie int not null,
	parse_par int not null,
	parse_bogey int not null,
	parse_dbogey int not null,
	parse_wbogey int not null,
	bogey_free boolean not null,
	made_cut boolean
	points int not null
	primary key (espn_event_id, espn_player_id, round_id)
);

create table sweepstakes.point_system (
	event_id int references events.events(event_id),
	points_per_hio int default=10,
	points_per_albatross int default=0,
	points_per_eagle int default=0,
	points_per_birdie int default=0,
	points_per_par int default=0,
	points_per_bogey int default=0,
	points_per_dbogey int default=0,
	points_per_wbogey int default=0,
	points_if_bogeyfree int default=2,
	points_if_madecut int default=5
);
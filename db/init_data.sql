-- Basic setup for key tables

-- CORE
insert into core.membership (member_type) values ('Full'),('Country'),('Visitor');


-- EVENTS
delete from events.series;
insert into events.series (series_id, series_name, series_year) values (gen_random_uuid(),'FedEx', 2025),(gen_random_uuid(),'Scrambles', 2025);
delete from events.event_types;
insert into events.event_types (event_type) values('Stableford'),('Stroke'),('Match'),('Sweepstakes'),('Scramble');
delete from events.tournaments;
insert into events.tournaments (tournament_id, series_id, tournament_name, tournament_start_date, tournament_end_date) values (gen_random_uuid(), (select distinct series_id from events.series where series_name = 'FedEx' and series_year = 2025), 'Tour - Bolton Old Links', make_date(2025,09,07), make_date(2025,09,07));
delete from events.courses;
insert into events.courses (course_id, golfcourseapi_course_id, club_name, course_location, course_holes, course_par, golfcourseapi_tee_data) values (gen_random_uuid(), <TBC>, 'Bolton Old Links', <TBC>, 18, <TBC>, <TBC>);
delete from events.events;
insert into events.events (event_id, event_type_id, tournament_id, event_name, course_id) values (gen_random_uuid(),1,(select distinct tournament_id from events.tournaments where tournament_name = 'Tour - Bolton Old Links'),'Bolton Old Links - Round 1',(select distinct course_id from events.courses where course_name = 'Bolton Old Links'))

-- SWEEPSTAKES
insert into users values (1, 'Luke',  'San Antonio',
                          'lukesanantonio@gmail.com', NULL);
insert into users values (2, 'Matt',  'Boutros', NULL, NULL);
insert into users values (3, 'David', 'Ibrahim', NULL, NULL);
insert into users values (4, 'Cloe',  'San Antonio', NULL, NULL);

insert into artists values (1, 'Bob Dylan', 1962, 'Class(y|ic) rock.');

insert into albums values (1, 'Tempest', 1, '2012-09-10');

insert into songs values (1,  'Duquesne Whistle', 1, 1, NULL, 99);
insert into songs values (2,  'Soon After Midnight', 1, 1, NULL, 99);
insert into songs values (3,  'Narrow Way', 1, 1, NULL, 99);
insert into songs values (4,  'Long and Wasted Years', 1, 1, NULL, 99);
insert into songs values (5,  'Pay in Blood', 1, 1, NULL, 99);
insert into songs values (6,  'Scarlet Town', 1, 1, NULL, 99);
insert into songs values (7,  'Early Roman Kings', 1, 1, NULL, 99);
insert into songs values (8,  'Tin Angel', 1, 1, NULL, 99);
insert into songs values (9,  'Tempest', 1, 1, NULL, 99);
insert into songs values (10, 'Roll on John', 1, 1, NULL, 99);

insert into artists values (2, 'Grouplove', 2009, 'Indie pop.');

insert into albums values (2, 'Never Trust a Happy Song', 2, '2011-09-13');

insert into songs values (11, 'Itchin'' on a Photograph', 2, 2, NULL, 99);
insert into songs values (12, 'Tongue Tied', 2, 2, NULL, 99);
insert into songs values (13, 'Lovely Cup', 2, 2, NULL, 99);
insert into songs values (14, 'Colours', 2, 2, NULL, 99);
insert into songs values (15, 'Slow', 2, 2, NULL, 99);
insert into songs values (16, 'Naked Kids', 2, 2, NULL, 99);
insert into songs values (17, 'Spun', 2, 2, NULL, 99);
insert into songs values (18, 'Betty''s a Bomb Shell', 2, 2, NULL, 99);
insert into songs values (19, 'Chloe', 2, 2, NULL, 99);
insert into songs values (20, 'Love Will Save Your Soul', 2, 2, NULL, 99);
insert into songs values (21, 'Cruel and Beautiful World', 2, 2, NULL, 99);
insert into songs values (22, 'Close Your Eyes and Count to Ten', 2, 2, NULL, 99);

insert into albums values (3, 'Spreading Rumors (Deluxe)', 2, '2013-09-17');

insert into songs values (23, 'I''m With You', 2, 3, NULL, 99);
insert into songs values (24, 'Borderlines and Aliens', 2, 3, NULL, 99);
insert into songs values (25, 'Schoolboy', 2, 3, NULL, 99);
insert into songs values (26, 'Ways To Go', 2, 3, NULL, 99);
insert into songs values (27, 'Shark Attack', 2, 3, NULL, 99);
insert into songs values (28, 'Sit Still', 2, 3, NULL, 99);
insert into songs values (29, 'Happy Hill', 2, 3, NULL, 99);
insert into songs values (30, 'What I Know', 2, 3, NULL, 99);
insert into songs values (31, 'Didn''t Have To Go', 2, 3, NULL, 99);
insert into songs values (32, 'Bitin'' The Bullet', 2, 3, NULL, 99);
insert into songs values (33, 'News To Me', 2, 3, NULL, 99);
insert into songs values (34, 'Raspberry', 2, 3, NULL, 99);
insert into songs values (35, 'Save The Party For Me', 2, 3, NULL, 99);
insert into songs values (36, 'Girl - Bonus Track', 2, 3, NULL, 99);
insert into songs values (37, 'Flowers - Bonus Track', 2, 3, NULL, 99);
insert into songs values (38, 'Beans On Pizza - Bonus Track', 2, 3, NULL, 99);

select setval('users_id_seq', 4);
select setval('artists_id_seq', 2);
select setval('albums_id_seq', 3);
select setval('songs_id_seq', 38);


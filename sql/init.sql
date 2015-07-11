create table users (
  id serial primary key,
  first_name text,
  last_name text,
  email text,
  password bytea
);

create table artists (
  id serial primary key,
  name text,
  formation_year smallint,
  bio TEXT
);
create table artist_users (
  artist_id integer references artists(id) on delete cascade,
  user_id integer references users(id) on delete cascade
);
create table albums (
  id serial primary key,
  name text,
  artist_id integer references artists(id),
  release_date text
);
create table songs (
  id serial primary key,
  name text,
  artist_id integer references artists(id),
  album_id integer references albums(id),
  hash bytea,
  price smallint
);

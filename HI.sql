CREATE TABLE users_final (
    id TEXT PRIMARY KEY,
    password TEXT,
    name TEXT,
    location TEXT,
    email text,
    provider text
);

select * from users_final;

create table being_test (
    id serial primary key,
    title text,
    summary text,
    period text,
    link text,
    genre text,
    region text
);

select * from being_test;
-- liquibase formatted sql

-- changeset tvkuvatov@edu.hse.ru:create-dashboards
-- comment: Create dashboard table
create table if not exists dashboards
(
    id   uuid primary key,
    name text not null
);
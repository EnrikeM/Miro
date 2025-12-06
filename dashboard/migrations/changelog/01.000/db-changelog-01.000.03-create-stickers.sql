-- liquibase formatted sql

-- changeset tvkuvatov@edu.hse.ru:create-stickers
-- comment: Create sticker table
create table if not exists stickers
(
    id           uuid primary key,
    dashboard_id uuid not null,
    x            integer,
    y            integer,
    text         text,
    width        integer,
    height       integer,
    color        text,
    constraint fk_sticker_dashboard foreign key (dashboard_id) references dashboards (id) on delete cascade
);

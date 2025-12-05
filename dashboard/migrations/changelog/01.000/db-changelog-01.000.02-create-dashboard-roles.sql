-- liquibase formatted sql

-- changeset tvkuvatov@edu.hse.ru:create-dashboard-roles
-- comment: Create dashboard_roles table
create table if not exists dashboard_roles
(
    dashboard_id uuid    not null,
    user_id      uuid    not null,
    user_role    text    not null check (user_role in ('owner', 'editor', 'viewer')),
    constraint pk_dashboard_roles primary key (dashboard_id, user_id),
    constraint fk_dashboard_roles_dashboard foreign key (dashboard_id) references dashboards (id) on delete cascade
);

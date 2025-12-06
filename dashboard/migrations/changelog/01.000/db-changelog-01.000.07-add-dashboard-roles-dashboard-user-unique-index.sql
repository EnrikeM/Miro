-- liquibase formatted sql

-- changeset tvkuvatov@edu.hse.ru:add-dashboard-roles-dashboard-user-unique-index
-- comment: Create sticker table
CREATE INDEX IF NOT EXISTS idx_dashboard_roles_dashboard_user_unique ON dashboard_roles USING btree (dashboard_id, user_id);
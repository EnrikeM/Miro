-- liquibase formatted sql

-- changeset tvkuvatov@edu.hse.ru:add-dashboard-roles-user_id-index
-- comment: Create sticker table
CREATE INDEX IF NOT EXISTS idx_dashboard_roles_user_id ON dashboard_roles USING btree (user_id);
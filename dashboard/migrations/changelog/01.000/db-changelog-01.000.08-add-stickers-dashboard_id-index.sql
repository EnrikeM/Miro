-- liquibase formatted sql

-- changeset tvkuvatov@edu.hse.ru:add-stickers-dashboard_id-index
-- comment: Create sticker table
CREATE INDEX IF NOT EXISTS idx_stickers_dashboard_id ON stickers USING btree (dashboard_id);
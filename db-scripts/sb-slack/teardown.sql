
DROP FUNCTION IF EXISTS authorize;
DROP FUNCTION IF EXISTS handle_new_user;
DROP TRIGGER IF EXISTS on_auth_user_created;

DROP TABLE IF EXISTS role_permissions CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS channels CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP TYPE IF EXISTS user_status CASCADE;
DROP TYPE IF EXISTS app_role CASCADE;
DROP TYPE IF EXISTS app_permission CASCADE;

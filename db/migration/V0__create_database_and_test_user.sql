-- transactional: false
-- Initial database and test user setup
-- Run this before V1__create_tables.sql with a MySQL account that can create databases and users.

CREATE DATABASE IF NOT EXISTS `skn34_1st_5team`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'skn34_test_user'@'%'
IDENTIFIED BY 'skn34_test_password';

GRANT ALL PRIVILEGES ON `skn34_1st_5team`.*
TO 'skn34_test_user'@'%';

FLUSH PRIVILEGES;

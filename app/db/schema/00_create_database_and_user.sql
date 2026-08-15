-- Run in MySQL Workbench as root (or another admin user).
-- Creates the database and restricted application user for local development.

CREATE DATABASE IF NOT EXISTS student_support
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Replace the password below before running, then use the same value in .env
CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY 'root';

GRANT SELECT, INSERT, UPDATE
    ON student_support.*
    TO 'root'@'localhost';

FLUSH PRIVILEGES;

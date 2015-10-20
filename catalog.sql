-- Table definitions for the tournament project.
-- psql -f catalog.sql
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'catalog'
AND pid <> pg_backend_pid();
DROP DATABASE catalog;
CREATE DATABASE catalog;
\c catalog;

CREATE TABLE categories (name VARCHAR(150) NOT NULL UNIQUE,
                         id serial PRIMARY KEY);

CREATE TABLE subcategories (name VARCHAR(350) UNIQUE,
                            category_id int REFERENCES categories(id),
                            id serial PRIMARY KEY
                            );

CREATE TABLE items (name VARCHAR(350) UNIQUE,
                   description VARCHAR(10485760),
                   AIN VARCHAR(150) PRIMARY KEY,
                   subcategory_id int REFERENCES subcategories(id),
                   image VARCHAR(150)
                  );

CREATE VIEW all_categories AS
    SELECT name FROM categories
    WHERE name != 'All';

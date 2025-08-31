DROP DATABASE IF EXISTS moviesdb;
CREATE DATABASE moviesdb;
USE moviesdb;

CREATE TABLE movies (
	     id INT AUTO_INCREMENT PRIMARY KEY, 
		 title VARCHAR(255) NOT NULL,
         genre VARCHAR(100),
         year INT
);

INSERT INTO movies (title, genre, year) VALUES ('The Matrix', 'Sci-Fi', 1999);
INSERT INTO movies (title, genre, year) VALUES ('Inception', 'Sci-Fi', 2010);
INSERT INTO movies (title, genre, year) VALUES ('The Dark Knight', 'Action', 2008);
INSERT INTO movies (title, genre, year) VALUES ('Interstellar', 'Sci-Fi', 2014);
INSERT INTO movies (title, genre, year) VALUES ('Gladiator', 'Action', 2000);

SELECT * FROM movies;

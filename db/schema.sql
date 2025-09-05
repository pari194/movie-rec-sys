DROP DATABASE IF EXISTS moviesdb;
CREATE DATABASE moviesdb;
USE moviesdb;

CREATE TABLE movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    year INT,
    director VARCHAR(100),
    rating FLOAT
);

INSERT INTO movies (title, genre, year, director, rating) VALUES 
('The Matrix', 'Sci-Fi', 1999, 'Lana Wachowski, Lilly Wachowski', 8.7),
('Inception', 'Sci-Fi', 2010, 'Christopher Nolan', 8.8),
('The Dark Knight', 'Action', 2008, 'Christopher Nolan', 9.0),
('Interstellar', 'Sci-Fi', 2014, 'Christopher Nolan', 8.6),
('Gladiator', 'Action', 2000, 'Ridley Scott', 8.5),
('The Shawshank Redemption', 'Drama', 1994, 'Frank Darabont', 9.3),
('Pulp Fiction', 'Crime', 1994, 'Quentin Tarantino', 8.9),
('Forrest Gump', 'Drama', 1994, 'Robert Zemeckis', 8.8),
('The Godfather', 'Crime', 1972, 'Francis Ford Coppala', 9.2),
('The Lord of the Rings: The Fellowship of the Ring', 'Fantasy', 2001, 'Peter Jackson', 8.8),
('Fight Club', 'Drama', 1999, 'David Fincher', 8.8),
('Goodfellas', 'Crime', 1990, 'Martin Scorsese', 8.7),
('The Silence of the Lambs', 'Thriller', 1991, 'Jonathan Demme', 8.6),
('Star Wars: Episode IV - A New Hope', 'Sci-Fi', 1977, 'George Lucas', 8.6),
('The Avengers', 'Action', 2012, 'Joss Whedon', 8.0);
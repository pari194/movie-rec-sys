import pandas as pd
import sqlite3
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import argparse
import json
import boto3
from botocore.exceptions import NoCredentialsError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MovieRecommendationSystem:
    def __init__(self, config_file='config.json'):
        """
        Initialize the recommendation system with SQLite
        """
        self.config = self.load_config(config_file)
        self.db_path = 'movies.db'
        self.df = None
        self.cosine_sim = None
        self.init_database()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using default configuration.")
            return {
                "aws": {
                    "s3_bucket": "your-movie-recommendation-bucket",
                    "region": "us-east-1"
                }
            }
    
    def init_database(self):
        """Initialize SQLite database with sample data"""
        # Create database connection
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create movies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                genre TEXT,
                year INTEGER,
                director TEXT,
                rating REAL
            )
        ''')
        
        # Insert sample data
        movies = [
            ('The Matrix', 'Sci-Fi', 1999, 'Lana Wachowski, Lilly Wachowski', 8.7),
            ('Inception', 'Sci-Fi', 2010, 'Christopher Nolan', 8.8),
            ('The Dark Knight', 'Action', 2008, 'Christopher Nolan', 9.0),
            ('Interstellar', 'Sci-Fi', 2014, 'Christopher Nolan', 8.6),
            ('Gladiator', 'Action', 2000, 'Ridley Scott', 8.5),
            ('The Shawshank Redemption', 'Drama', 1994, 'Frank Darabont', 9.3),
            ('Pulp Fiction', 'Crime', 1994, 'Quentin Tarantino', 8.9),
            ('Forrest Gump', 'Drama', 1994, 'Robert Zemeckis', 8.8),
            ('The Godfather', 'Crime', 1972, 'Francis Ford Coppola', 9.2),
            ('The Lord of the Rings: The Fellowship of the Ring', 'Fantasy', 2001, 'Peter Jackson', 8.8),
            ('Fight Club', 'Drama', 1999, 'David Fincher', 8.8),
            ('Goodfellas', 'Crime', 1990, 'Martin Scorsese', 8.7),
            ('The Silence of the Lambs', 'Thriller', 1991, 'Jonathan Demme', 8.6),
            ('Star Wars: Episode IV - A New Hope', 'Sci-Fi', 1977, 'George Lucas', 8.6),
            ('The Avengers', 'Action', 2012, 'Joss Whedon', 8.0)
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO movies (title, genre, year, director, rating)
            VALUES (?, ?, ?, ?, ?)
        ''', movies)
        
        conn.commit()
        conn.close()
        logger.info("SQLite database initialized with sample data")
    
    def get_movie_data(self):
        """Retrieve movie data from SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT title, genre, year, director, rating FROM movies", conn)
            conn.close()
            logger.info(f"Retrieved {len(df)} movies from database")
            return df
        except sqlite3.Error as err:
            logger.error(f"Failed to retrieve data: {err}")
            return None
    
    def setup_recommendation_system(self):
        """Setup the recommendation system with vectorization"""
        self.df = self.get_movie_data()
        if self.df is None:
            logger.error("Failed to get movie data")
            return False
        
        # Create features by combining genre, year, director, and rating
        self.df["features"] = (
            self.df["genre"] + " " + 
            self.df["year"].astype(str) + " " + 
            self.df["director"].fillna("") + " " + 
            self.df["rating"].astype(str)
        )
        
        # Vectorize features
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(self.df["features"])
        self.cosine_sim = cosine_similarity(count_matrix)
        
        logger.info("Recommendation system setup completed")
        return True
    
    def recommend(self, movie_title, num_recommendations=5):
        """
        Get recommendations for a movie
        
        Args:
            movie_title (str): Title of the movie to get recommendations for
            num_recommendations (int): Number of recommendations to return
            
        Returns:
            list: Recommended movie titles
        """
        if self.df is None or self.cosine_sim is None:
            if not self.setup_recommendation_system():
                return ["System not initialized"]
        
        if movie_title not in self.df["title"].values:
            return ["Movie not found in database!"]
        
        idx = self.df[self.df.title == movie_title].index[0]
        scores = list(enumerate(self.cosine_sim[idx]))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        
        # Get recommendations (skip the first as it's the same movie)
        recommendations = []
        for i in sorted_scores[1:num_recommendations+1]:
            movie_data = self.df.iloc[i[0]]
            recommendations.append({
                'title': movie_data['title'],
                'genre': movie_data['genre'],
                'year': movie_data['year'],
                'director': movie_data['director'],
                'rating': movie_data['rating'],
                'similarity_score': i[1]
            })
        
        return recommendations
    
    def upload_to_s3(self, file_name, bucket_name=None):
        """
        Upload a file to AWS S3
        
        Args:
            file_name (str): Name of the file to upload
            bucket_name (str): Name of the S3 bucket
            
        Returns:
            bool: True if upload was successful, False otherwise
        """
        if bucket_name is None:
            bucket_name = self.config['aws'].get('s3_bucket', 'your-movie-recommendation-bucket')
        
        try:
            s3 = boto3.client('s3')
            s3.upload_file(file_name, bucket_name, file_name)
            logger.info(f"Successfully uploaded {file_name} to S3 bucket {bucket_name}")
            return True
        except FileNotFoundError:
            logger.error(f"The file {file_name} was not found")
            return False
        except NoCredentialsError:
            logger.error("AWS credentials not available")
            return False
    
    def export_recommendations(self, movie_title, num_recommendations=5, format='json'):
        """
        Export recommendations to a file
        
        Args:
            movie_title (str): Title of the movie to get recommendations for
            num_recommendations (int): Number of recommendations to return
            format (str): Output format ('json' or 'csv')
            
        Returns:
            str: Name of the exported file
        """
        recommendations = self.recommend(movie_title, num_recommendations)
        
        if format == 'json':
            file_name = f"{movie_title.replace(' ', '_')}_recommendations.json"
            with open(file_name, 'w') as f:
                json.dump({
                    'input_movie': movie_title,
                    'recommendations': recommendations
                }, f, indent=2)
        else:  # csv
            file_name = f"{movie_title.replace(' ', '_')}_recommendations.csv"
            df = pd.DataFrame(recommendations)
            df.to_csv(file_name, index=False)
        
        logger.info(f"Recommendations exported to {file_name}")
        return file_name

def main():
    """Main function to run the recommendation system"""
    parser = argparse.ArgumentParser(description='Movie Recommendation System')
    parser.add_argument('--movie', type=str, help='Movie title to get recommendations for')
    parser.add_argument('--num', type=int, default=5, help='Number of recommendations (default: 5)')
    parser.add_argument('--export', type=str, choices=['json', 'csv'], help='Export format')
    parser.add_argument('--upload', action='store_true', help='Upload to AWS S3 after export')
    parser.add_argument('--list', action='store_true', help='List all available movies')
    
    args = parser.parse_args()
    
    # Initialize the recommendation system
    recommender = MovieRecommendationSystem()
    
    # List all available movies
    if args.list:
        df = recommender.get_movie_data()
        if df is not None:
            print("Available movies:")
            for _, row in df.iterrows():
                print(f"- {row['title']} ({row['year']}), Genre: {row['genre']}, Rating: {row['rating']}")
        return
    
    # Get recommendations for a specific movie
    if args.movie:
        recommendations = recommender.recommend(args.movie, args.num)
        
        if recommendations and isinstance(recommendations, list) and recommendations[0] != "Movie not found in database!":
            print(f"\nRecommendations for '{args.movie}':")
            print("=" * 50)
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['title']} ({rec['year']})")
                print(f"   Genre: {rec['genre']}, Director: {rec['director']}, Rating: {rec['rating']}")
                print(f"   Similarity Score: {rec['similarity_score']:.4f}")
                print()
            
            # Export if requested
            if args.export:
                file_name = recommender.export_recommendations(args.movie, args.num, args.export)
                
                # Upload to S3 if requested
                if args.upload:
                    recommender.upload_to_s3(file_name)
        else:
            print(f"Movie '{args.movie}' not found in the database.")
            
            # Show available movies
            if recommender.df is not None:
                print("\nAvailable movies:")
                for title in recommender.df['title'].values:
                    print(f"- {title}")
    else:
        print("Please specify a movie title using --movie argument")
        print("Use --list to see all available movies")

if __name__ == "__main__":
    main()
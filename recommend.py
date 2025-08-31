import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import mysql.connector

def get_movie_data():
    # Connect to DB - USE YOUR ACTUAL PASSWORD
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_actual_password_here",  # CHANGE THIS
        database="moviesdb"
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT title, genre, year FROM movies")
    rows = cursor.fetchall()
    conn.close()
    
    return pd.DataFrame(rows, columns=["title", "genre", "year"])

def setup_recommendation_system():
    df = get_movie_data()
    df["features"] = df["genre"] + " " + df["year"].astype(str)
    
    # Vectorize
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["features"])
    cosine_sim = cosine_similarity(count_matrix)
    
    return df, cosine_sim

def recommend(movie_title, df, cosine_sim):
    if movie_title not in df["title"].values:
        return ["Movie not found!"]
    
    idx = df[df.title == movie_title].index[0]
    scores = list(enumerate(cosine_sim[idx]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    
    # Get recommendations
    recommendations = []
    for i in sorted_scores[1:]:  # Skip the first (same movie)
        if len(recommendations) >= 4:  # Get up to 4 recommendations
            break
        recommendations.append(df.iloc[i[0]].title)
    
    return recommendations

def main():
    # Setup the system
    df, cosine_sim = setup_recommendation_system()
    
    # Get user input
    movie = input("Enter a movie title: ")
    
    # Get and display recommendations
    recommendations = recommend(movie, df, cosine_sim)
    print("Recommendations:", recommendations)

if _name_ == "_main_":
    main()

#!/usr/bin/env python3
"""
Main script to run the Movie Recommendation System
"""

from ai.recommend import MovieRecommendationSystem
import argparse

def main():
    parser = argparse.ArgumentParser(description='Movie Recommendation System')
    parser.add_argument('--movie', type=str, required=True, help='Movie title to get recommendations for')
    parser.add_argument('--num', type=int, default=5, help='Number of recommendations')
    
    args = parser.parse_args()
    
    recommender = MovieRecommendationSystem()
    recommendations = recommender.recommend(args.movie, args.num)
    
    print(f"Recommendations for '{args.movie}':")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']} ({rec['year']}) - {rec['genre']}")

if __name__ == "__main__":
    main()
# 🎬 Movie Recommendation System (AI + SQL + Python + AWS)

A simple AI-powered Movie Recommendation System.

## Features
- MySQL for storing movies
- AI (cosine similarity) for recommendations
- Python backend
- Cloud-ready (AWS RDS + EC2)

## Run Locally
```bash
pip install -r requirements.txt
mysql -u root -p < db/schema.sql
python ai/recommend.py
```
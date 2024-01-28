from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from models import Base, VideosTable

# Get the environment variables
POSTGRES_URL = os.environ.get('POSTGRES_URL', None)

if POSTGRES_URL is None:
    print("POSTGRES_URL environment variable not set")
    exit(1)

# Create the engine to connect to the PostgreSQL database
engine = create_engine(POSTGRES_URL)
Base.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/videos')
def get_videos():
    videos = session.query(VideosTable).all()
    return str(videos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)


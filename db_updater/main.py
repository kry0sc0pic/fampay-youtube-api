import os
import time

import requests
from typing import Union
from helpers import datetime_to_iso
from models import Base, VideosTable
from sqlalchemy import create_engine, desc
import datetime
from sqlalchemy.orm import sessionmaker
from helpers import get_videos, get_video_full_description

### Database Connection ###
QUERY = "financial news"
# POSTGRES_URL = os.environ.get('POSTGRES_URL', None)
POSTGRES_URL = "postgresql://postgres:lLhi3zdgLRQjLfz@localhost:5432/postgres"

# Connect to Postgres
engine = create_engine(POSTGRES_URL)

# Create tables if they don't exist
Base.metadata.create_all(engine, checkfirst=True)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

lastRecord = session.query(VideosTable).order_by(desc(VideosTable.publishedAt)).first()
retrieveAll = lastRecord is not None  # should retrieve all the videos if continuing from database. Otherwise only load a few to init database
if lastRecord:
    lastTimeStamp = datetime_to_iso(lastRecord.publishedAt)
else:
    lastTimeStamp = datetime_to_iso(datetime.datetime.now() - datetime.timedelta(days=1))

while True:
    if retrieveAll:
        print(f"Retrieving all videos after {lastTimeStamp}")
        videos = get_videos(QUERY, lastTimeStamp, key="AIzaSyBR01jXPiKS5MsyNPSXXxB1BzPiIOjfqUI", limit=-1)
        print(f"Retrieved a total of {len(videos)} videos")
    else:
        print(f"Retrieving 200 initial videos after {lastTimeStamp}")
        retrieveAll = True
        videos = get_videos(QUERY, lastTimeStamp, key="AIzaSyBR01jXPiKS5MsyNPSXXxB1BzPiIOjfqUI", limit=200)
        print(f"Retrieved a total of {len(videos)} videos")
    updated = False
    i = 1
    for video in videos:
        description = video['snippet']['description']
        if description.endswith(' ...'):
            print(f"Incomplete {video['id']['videoId']}")
            full_description = get_video_full_description(video['id']['videoId'],
                                                          key="AIzaSyBR01jXPiKS5MsyNPSXXxB1BzPiIOjfqUI")
            if full_description is not None:
                print(f"Full description retrieved")
                description = full_description
            else:
                print("Full description retrieval failed")
        else:
            print("Full description already retrieved")
        video_data = {
            'videoId': video['id']['videoId'],
            'title': video['snippet']['title'],
            'description': description,
            'publishedAt': datetime.datetime.fromisoformat(video['snippet']['publishedAt'][:-1]),
            'channelId': video['snippet']['channelId'],
            'channelTitle': video['snippet']['channelTitle'],
            'thumbnail': video['snippet']['thumbnails']['high']['url'],
        }
        video_record = VideosTable(**video_data)
        print(f"{i}/{len(videos)} | Adding video {video['id']['videoId']} to database")
        i+=1
        session.merge(video_record)
        if not updated:
            lastTimeStamp = video['snippet']['publishedAt']
            updated = True
    print("Committing changes")
    session.commit()
    print("Closing session")
    session.close()
    print("Sleeping for 10 seconds")
    exit(0)
    time.sleep(10)

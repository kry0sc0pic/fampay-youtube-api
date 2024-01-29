import time
from helpers import datetime_to_iso
from models import Base, VideosTable
from sqlalchemy import create_engine, desc
import datetime
from sqlalchemy.orm import sessionmaker
from helpers import get_videos, get_video_full_description, iso_increment
from key_provider import KeyProvider
import redis
import os

QUERY = "financial news"  # query to search for. (maybe move this to an environment variable or config file later?)

keyProvider = KeyProvider()  # key provider to handle key rotation

# PostgreSQL Setup
POSTGRES_URL = os.environ.get("POSTGRES_URL", None)
engine = create_engine(POSTGRES_URL)
Base.metadata.create_all(engine, checkfirst=True)
Session = sessionmaker(bind=engine)
session = Session()

# Connect to Redis
redisClient = redis.Redis(
    os.environ.get("REDIS_HOST", "localhost"),
    port=os.environ.get("REDIS_PORT", 6379),
    db=os.environ.get("REDIS_DB", 0),
    decode_responses=True,
)

# Check if database has any records
lastRecord = session.query(VideosTable).order_by(desc(VideosTable.publishedAt)).first()

retrieveAll = (
    lastRecord is not None
)  # should retrieve all the videos if continuing from database. Otherwise only
# load a few to init database
if lastRecord:
    lastTimeStamp = datetime_to_iso(lastRecord.publishedAt)
else:
    lastTimeStamp = datetime_to_iso(
        datetime.datetime.now() - datetime.timedelta(days=1)
    )

while True:
    # used for all checks after database has initial set of records
    if retrieveAll:
        print(f"Retrieving all videos after {lastTimeStamp}")
        videos = get_videos(
            QUERY, lastTimeStamp, key_provider=keyProvider, limit=-1
        )
        print(f"Retrieved a total of {len(videos)} videos")
    # used to initialize database with a maximum of 200 uploads after yesterday.
    else:
        print(f"Retrieving 50 initial videos after {lastTimeStamp}")
        retrieveAll = True
        videos = get_videos(
            QUERY, lastTimeStamp, key_provider=keyProvider, limit=50
        )
        print(f"Retrieved a total of {len(videos)} videos")
    updated = False
    i = 1

    for video in videos:
        description = video["snippet"]["description"]
        """Some descriptions are truncated by the Youtube Search API in the snippet. This description field in the 
        snippet ends with ' ...' to indicate that it was truncated.
        
        If the description is truncated, we need to retrieve the full description from the video resource endpoint.
        """
        if description.endswith(
            " ..."
        ):  # end with ... means the description was truncated
            print(f"Incomplete description for video {video['id']['videoId']}")
            full_description = get_video_full_description(
                video["id"]["videoId"], key_provider=keyProvider
            )
            if full_description is not None:
                print(f"Full description retrieved")
                description = full_description
            else:
                print("Full description retrieval failed")
        else:
            print("Full description already retrieved")
        video_data = {
            "videoId": video["id"]["videoId"],
            "title": video["snippet"]["title"],
            "description": description,
            "publishedAt": datetime.datetime.fromisoformat(
                video["snippet"]["publishedAt"][:-1]
            ),
            "channelId": video["snippet"]["channelId"],
            "channelTitle": video["snippet"]["channelTitle"],
            "thumbnail": video["snippet"]["thumbnails"]["high"]["url"],
        }
        video_record = VideosTable(**video_data)
        print(f"{i}/{len(videos)} | Adding video {video['id']['videoId']} to database")
        i += 1
        session.merge(video_record)
        if not updated:
            lastTimeStamp = iso_increment(video["snippet"]["publishedAt"])
            updated = True
    if len(videos) > 0:
        print("Committing changes")
        session.commit()
        print("Closing session")
        session.close()
        print("Clearing Redis Cache")
        for key in redisClient.keys():
            redisClient.delete(key)
    print("Sleeping for 10 seconds")
    time.sleep(10)
